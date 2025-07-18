import warnings
from typing import Optional, Union

import ee

from ee_extra.STAC.utils import _get_platform_STAC


def maskClouds(
    x: Union[ee.Image, ee.ImageCollection],
    method: str = "cloud_prob",
    prob: Union[int, float] = 60,
    maskCirrus: bool = True,
    maskShadows: bool = True,
    scaledImage: bool = False,
    dark: float = 0.15,
    cloudDist: int = 1000,
    buffer: int = 250,
    cdi: Optional[float] = None,
) -> Union[ee.Image, ee.ImageCollection]:
    """Masks clouds and shadows in an image or image collection (valid just for Surface Reflectance products).

    Parameters:
        x : Image or Image Collection to mask.
        method : Method used to mask clouds.\n
            Available options:
                - 'cloud_prob' : Use cloud probability.
                - 'cloud_score+' : Use cloud score+.
                - 'qa' : Use Quality Assessment band.
            This parameter is ignored for Landsat products.
        prob : Cloud probability threshold. Valid for method = 'cloud_prob' or 'cloud_score+'. This parameter is ignored for Landsat products.
        maskCirrus : Whether to mask cirrus clouds. Valid just for method = 'qa'. This parameter is ignored for Landsat products.
        maskShadows : Whether to mask cloud shadows. For more info see 'Braaten, J. 2020. Sentinel-2 Cloud Masking with s2cloudless. Google Earth Engine, Community Tutorials'.
        scaledImage : Whether the pixel values are scaled to the range [0,1] (reflectance values). This parameter is ignored for Landsat products.
        dark : NIR threshold. NIR values below this threshold are potential cloud shadows. This parameter is ignored for Landsat products.
        cloudDist : Maximum distance in meters (m) to look for cloud shadows from cloud edges. This parameter is ignored for Landsat products.
        buffer : Distance in meters (m) to dilate cloud and cloud shadows objects. This parameter is ignored for Landsat products.
        cdi : Cloud Displacement Index threshold. Values below this threshold are considered potential clouds.
            A cdi = None means that the index is not used. For more info see 'Frantz, D., HaS, E., Uhl, A., Stoffels, J., Hill, J. 2018. Improvement of the Fmask algorithm for Sentinel-2 images:
            Separating clouds from bright surfaces based on parallax effects. Remote Sensing of Environment 2015: 471-481'.
            This parameter is ignored for Landsat products.

    Returns:
        Cloud-shadow masked image or image collection.
    """

    validMethods = ["cloud_prob", "cloud_score+", "qa"]

    if method not in validMethods:
        raise Exception(
            f"'{method}' is not a valid method. Please use one of {validMethods}."
        )

    def S3(args):
        qa = args.select("quality_flags")
        notCloud = qa.bitwiseAnd(1 << 27).eq(0)
        return args.updateMask(notCloud)

    def S2(args):
        def cloud_prob(img):
            clouds = ee.Image(img.get("cloud_mask")).select("probability")
            isCloud = clouds.gte(prob).rename("CLOUD_MASK")
            return img.addBands(isCloud)
        
        def cloud_score(img):
            clouds = img.select("cs_cdf")
            isCloud = clouds.lte(1-(prob/100)).rename("CLOUD_MASK")
            return img.addBands(isCloud)

        def QA(img):
            qa = img.select("QA60")
            cloudBitMask = 1 << 10
            isCloud = qa.bitwiseAnd(cloudBitMask).eq(0)
            if maskCirrus:
                cirrusBitMask = 1 << 11
                isCloud = isCloud.And(qa.bitwiseAnd(cirrusBitMask).eq(0))
            isCloud = isCloud.Not().rename("CLOUD_MASK")
            return img.addBands(isCloud)

        def CDI(img):
            idx = img.get("system:index")
            S2TOA = (
                ee.ImageCollection("COPERNICUS/S2")
                .filter(ee.Filter.eq("system:index", idx))
                .first()
            )
            CloudDisplacementIndex = ee.Algorithms.Sentinel2.CDI(S2TOA)
            isCloud = CloudDisplacementIndex.lt(cdi).rename("CLOUD_MASK_CDI")
            return img.addBands(isCloud)

        def get_shadows(img):
            notWater = img.select("SCL").neq(6)
            if not scaledImage:
                darkPixels = img.select("B8").lt(dark * 1e4).multiply(notWater)
            else:
                darkPixels = img.select("B8").lt(dark).multiply(notWater)
            shadowAzimuth = ee.Number(90).subtract(
                ee.Number(img.get("MEAN_SOLAR_AZIMUTH_ANGLE"))
            )
            cloudProjection = img.select("CLOUD_MASK").directionalDistanceTransform(
                shadowAzimuth, cloudDist / 10
            )
            cloudProjection = (
                cloudProjection.reproject(crs=img.select(0).projection(), scale=10)
                .select("distance")
                .mask()
            )
            isShadow = cloudProjection.multiply(darkPixels).rename("SHADOW_MASK")
            return img.addBands(isShadow)

        def clean_dilate(img):
            isCloudShadow = img.select("CLOUD_MASK")
            if cdi != None:
                isCloudShadow = isCloudShadow.And(img.select("CLOUD_MASK_CDI"))
            if maskShadows:
                isCloudShadow = isCloudShadow.add(img.select("SHADOW_MASK")).gt(0)
            isCloudShadow = (
                isCloudShadow.focal_min(20, units="meters")
                .focal_max(buffer * 2 / 10, units="meters")
                .rename("CLOUD_SHADOW_MASK")
            )
            return img.addBands(isCloudShadow)

        def apply_mask(img):
            return img.updateMask(img.select("CLOUD_SHADOW_MASK").Not())

        if isinstance(x, ee.image.Image):
            if method == "cloud_prob":
                S2Clouds = ee.ImageCollection("COPERNICUS/S2_CLOUD_PROBABILITY")
                fil = ee.Filter.equals(
                    leftField="system:index", rightField="system:index"
                )
                S2WithCloudMask = ee.Join.saveFirst("cloud_mask").apply(
                    ee.ImageCollection(args), S2Clouds, fil
                )
                S2Masked = ee.ImageCollection(S2WithCloudMask).map(cloud_prob).first()
            elif method == 'cloud_score+':
                QA_BAND = 'cs_cdf'
                S2Clouds = ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED').select(QA_BAND)
                S2WithCloudMask = ee.ImageCollection(args).linkCollection(S2Clouds, [QA_BAND])
                S2Masked = ee.ImageCollection(S2WithCloudMask).map(cloud_score).first()
            elif method == "qa":
                S2Masked = QA(args)
            if cdi != None:
                S2Masked = CDI(S2Masked)
            if maskShadows:
                S2Masked = get_shadows(S2Masked)
            S2Masked = apply_mask(clean_dilate(S2Masked))
        elif isinstance(x, ee.imagecollection.ImageCollection):
            if method == "cloud_prob":
                S2Clouds = ee.ImageCollection("COPERNICUS/S2_CLOUD_PROBABILITY")
                fil = ee.Filter.equals(
                    leftField="system:index", rightField="system:index"
                )
                S2WithCloudMask = ee.Join.saveFirst("cloud_mask").apply(
                    args, S2Clouds, fil
                )
                S2Masked = ee.ImageCollection(S2WithCloudMask).map(cloud_prob)
            elif method == 'cloud_score+':
                QA_BAND = 'cs_cdf'
                S2Clouds = ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED').select(QA_BAND)
                S2WithCloudMask = ee.ImageCollection(args).linkCollection(S2Clouds, [QA_BAND])
                S2Masked = ee.ImageCollection(S2WithCloudMask).map(cloud_score)
            elif method == "qa":
                S2Masked = args.map(QA)
            if cdi != None:
                S2Masked = S2Masked.map(CDI)
            if maskShadows:
                S2Masked = S2Masked.map(get_shadows)
            S2Masked = S2Masked.map(clean_dilate).map(apply_mask)

        return S2Masked

    def L8(args):
        cloudsBitMask = 1 << 5
        qa = args.select("pixel_qa")
        mask = qa.bitwiseAnd(cloudsBitMask).eq(0)
        if maskShadows:
            cloudShadowBitMask = 1 << 3
            mask = mask.And(qa.bitwiseAnd(cloudShadowBitMask).eq(0))
        return args.updateMask(mask)

    def L8C2(args):
        qa = args.select("QA_PIXEL")
        notCloud = qa.bitwiseAnd(1 << 3).eq(0)
        if maskShadows:
            notCloud = notCloud.And(qa.bitwiseAnd(1 << 4).eq(0))
        if maskCirrus:
            notCloud = notCloud.And(qa.bitwiseAnd(1 << 2).eq(0))
        return args.updateMask(notCloud)

    def L457(args):
        qa = args.select("pixel_qa")
        cloud = qa.bitwiseAnd(1 << 5).And(qa.bitwiseAnd(1 << 7))
        if maskShadows:
            cloud = cloud.Or(qa.bitwiseAnd(1 << 3))
        mask2 = args.mask().reduce(ee.Reducer.min())
        return args.updateMask(cloud.Not()).updateMask(mask2)

    def L457C2(args):
        qa = args.select("QA_PIXEL")
        notCloud = qa.bitwiseAnd(1 << 3).eq(0)
        if maskShadows:
            notCloud = notCloud.And(qa.bitwiseAnd(1 << 4).eq(0))
        return args.updateMask(notCloud)

    def MOD09GA(args):
        qa = args.select("state_1km")
        notCloud = qa.bitwiseAnd(1 << 0).eq(0)
        if maskShadows:
            notCloud = notCloud.And(qa.bitwiseAnd(1 << 2).eq(0))
        if maskCirrus:
            notCloud = notCloud.And(qa.bitwiseAnd(1 << 8).eq(0))
        return args.updateMask(notCloud)

    def MCD15A3H(args):
        qa = args.select("FparExtra_QC")
        notCloud = qa.bitwiseAnd(1 << 5).eq(0)
        if maskShadows:
            notCloud = notCloud.And(qa.bitwiseAnd(1 << 6).eq(0))
        if maskCirrus:
            notCloud = notCloud.And(qa.bitwiseAnd(1 << 4).eq(0))
        return args.updateMask(notCloud)

    def MOD09Q1(args):
        qa = args.select("State")
        notCloud = qa.bitwiseAnd(1 << 0).eq(0)
        if maskShadows:
            notCloud = notCloud.And(qa.bitwiseAnd(1 << 2).eq(0))
        if maskCirrus:
            notCloud = notCloud.And(qa.bitwiseAnd(1 << 8).eq(0))
        return args.updateMask(notCloud)

    def MOD09A1(args):
        qa = args.select("StateQA")
        notCloud = qa.bitwiseAnd(1 << 0).eq(0)
        if maskShadows:
            notCloud = notCloud.And(qa.bitwiseAnd(1 << 2).eq(0))
        if maskCirrus:
            notCloud = notCloud.And(qa.bitwiseAnd(1 << 8).eq(0))
        return args.updateMask(notCloud)

    def MOD17A2H(args):
        qa = args.select("Psn_QC")
        notCloud = qa.bitwiseAnd(1 << 3).eq(0)
        return args.updateMask(notCloud)

    def MOD16A2(args):
        qa = args.select("ET_QC")
        notCloud = qa.bitwiseAnd(1 << 3).eq(0)
        return args.updateMask(notCloud)

    def MOD13Q1A1(args):
        qa = args.select("SummaryQA")
        notCloud = qa.bitwiseAnd(1 << 0).eq(0)
        return args.updateMask(notCloud)

    def MOD13A2(args):
        qa = args.select("SummaryQA")
        notCloud = qa.eq(0)
        return args.updateMask(notCloud)

    def VNP09GA(args):
        qf1 = args.select("QF1")
        qf2 = args.select("QF2")
        notCloud = qf1.bitwiseAnd(1 << 2).eq(0)
        if maskShadows:
            notCloud = notCloud.And(qf2.bitwiseAnd(1 << 3).eq(0))
        if maskCirrus:
            notCloud = notCloud.And(qf2.bitwiseAnd(1 << 6).eq(0))
            notCloud = notCloud.And(qf2.bitwiseAnd(1 << 7).eq(0))
        return args.updateMask(notCloud)

    def VNP13A1(args):
        qa = args.select("pixel_reliability")
        notCloud = qa.neq(9)
        if maskShadows:
            notCloud = notCloud.And(qa.neq(7))
        return args.updateMask(notCloud)

    lookup = {
        "COPERNICUS/S3/OLCI": S3,
        "COPERNICUS/S2_SR": S2,
        "COPERNICUS/S2_SR_HARMONIZED": S2,
        "LANDSAT/LC08/C01/T1_SR": L8,
        "LANDSAT/LC08/C01/T2_SR": L8,
        "LANDSAT/LC08/C02/T1_L2": L8C2,
        "LANDSAT/LC08/C02/T2_L2": L8C2,
        "LANDSAT/LC09/C02/T1_L2": L8C2,
        "LANDSAT/LC09/C02/T2_L2": L8C2,
        "LANDSAT/LE07/C01/T1_SR": L457,
        "LANDSAT/LE07/C01/T2_SR": L457,
        "LANDSAT/LE07/C02/T1_L2": L457C2,
        "LANDSAT/LE07/C02/T2_L2": L457C2,
        "LANDSAT/LT05/C01/T1_SR": L457,
        "LANDSAT/LT05/C01/T2_SR": L457,
        "LANDSAT/LT05/C02/T1_L2": L457C2,
        "LANDSAT/LT05/C02/T2_L2": L457C2,
        "LANDSAT/LT04/C01/T1_SR": L457,
        "LANDSAT/LT04/C01/T2_SR": L457,
        "LANDSAT/LT04/C02/T1_L2": L457C2,
        "LANDSAT/LT04/C02/T2_L2": L457C2,
        "MODIS/006/MOD09GA": MOD09GA,
        "MODIS/006/MCD15A3H": MCD15A3H,
        "MODIS/006/MOD09Q1": MOD09Q1,
        "MODIS/006/MOD09A1": MOD09A1,
        "MODIS/006/MOD17A2H": MOD17A2H,
        "MODIS/006/MOD16A2": MOD16A2,
        "MODIS/006/MOD13Q1": MOD13Q1A1,
        "MODIS/006/MOD13A1": MOD13Q1A1,
        "MODIS/006/MOD13A2": MOD13A2,
        "MODIS/006/MYD09GA": MOD09GA,
        "MODIS/006/MYD09Q1": MOD09Q1,
        "MODIS/006/MYD09A1": MOD09A1,
        "MODIS/006/MYD17A2H": MOD17A2H,
        "MODIS/006/MYD16A2": MOD16A2,
        "MODIS/006/MYD13Q1": MOD13Q1A1,
        "MODIS/006/MYD13A1": MOD13Q1A1,
        "MODIS/006/MYD13A2": MOD13A2,
        "MODIS/061/MOD09GA": MOD09GA,
        "MODIS/061/MCD15A3H": MCD15A3H,
        "MODIS/061/MOD09Q1": MOD09Q1,
        "MODIS/061/MOD09A1": MOD09A1,
        "MODIS/061/MOD17A2H": MOD17A2H,
        "MODIS/061/MOD16A2": MOD16A2,
        "MODIS/061/MOD13Q1": MOD13Q1A1,
        "MODIS/061/MOD13A1": MOD13Q1A1,
        "MODIS/061/MOD13A2": MOD13A2,
        "MODIS/061/MYD09GA": MOD09GA,
        "MODIS/061/MYD09Q1": MOD09Q1,
        "MODIS/061/MYD09A1": MOD09A1,
        "MODIS/061/MYD17A2H": MOD17A2H,
        "MODIS/061/MYD16A2": MOD16A2,
        "MODIS/061/MYD13Q1": MOD13Q1A1,
        "MODIS/061/MYD13A1": MOD13Q1A1,
        "MODIS/061/MYD13A2": MOD13A2,
        "NOAA/VIIRS/001/VNP09GA": VNP09GA,
        "NOAA/VIIRS/001/VNP13A1": VNP13A1,
    }

    platformDict = _get_platform_STAC(x)

    if platformDict["platform"] not in list(lookup.keys()):
        warnings.warn("This platform is not supported for cloud masking.")
        return x
    else:
        if isinstance(x, ee.image.Image):
            masked = lookup[platformDict["platform"]](x)
        elif isinstance(x, ee.imagecollection.ImageCollection):
            if platformDict["platform"] in ["COPERNICUS/S2_SR", "COPERNICUS/S2_SR_HARMONIZED"]:
                masked = lookup[platformDict["platform"]](x)
            else:
                masked = x.map(lookup[platformDict["platform"]])
        return masked

