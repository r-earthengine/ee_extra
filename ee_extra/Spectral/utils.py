import json
import os
import re
import urllib.request
import warnings
from typing import Optional, Union, Tuple, Dict

import ee
import pkg_resources

from ee_extra.STAC.utils import _get_platform_STAC
from ee_extra.utils import _load_JSON


def _get_expression_map(img: ee.Image, platformDict: dict) -> dict:
    """Gets the dictionary required for the map parameter i n ee.Image.expression() method.

    Args:
        img : Image to get the dictionary from.
        platformDict : Dictionary retrieved from the _get_STAC_platform() method.

    Returns:
        Map dictionary for the ee.Image.expression() method.
    """

    def lookupPALSAR(img):
        return {
            "HH": img.select("HH"),
            "HV": img.select("HV"),
        }

    def lookupS1(img):
        return {
            "HH": img.select("HH"),
            "HV": img.select("HV"),
            "VV": img.select("VV"),
            "VH": img.select("VH"),
        }

    def lookupS2(img):
        return {
            "A": img.select("B1"),
            "B": img.select("B2"),
            "G": img.select("B3"),
            "R": img.select("B4"),
            "RE1": img.select("B5"),
            "RE2": img.select("B6"),
            "RE3": img.select("B7"),
            "N": img.select("B8"),
            "N2": img.select("B8A"),
            "WV": img.select("B9"),
            "S1": img.select("B11"),
            "S2": img.select("B12"),
            "lambdaG": 559.8,
            "lambdaR": 664.6,
            "lambdaN": 832.8,
        }

    def lookupL8(img):
        return {
            "A": img.select("B1"),
            "B": img.select("B2"),
            "G": img.select("B3"),
            "R": img.select("B4"),
            "N": img.select("B5"),
            "S1": img.select("B6"),
            "S2": img.select("B7"),
            "T1": img.select("B10"),
            "T2": img.select("B11"),
            "lambdaG": 560.0,
            "lambdaR": 655.0,
            "lambdaN": 865.0,
        }

    def lookupL8C2(img):
        return {
            "A": img.select("SR_B1"),
            "B": img.select("SR_B2"),
            "G": img.select("SR_B3"),
            "R": img.select("SR_B4"),
            "N": img.select("SR_B5"),
            "S1": img.select("SR_B6"),
            "S2": img.select("SR_B7"),
            "T1": img.select("ST_B10"),
            "lambdaG": 560.0,
            "lambdaR": 655.0,
            "lambdaN": 865.0,
        }

    def lookupL45(img):
        return {
            "B": img.select("B1"),
            "G": img.select("B2"),
            "R": img.select("B3"),
            "N": img.select("B4"),
            "S1": img.select("B5"),
            "T1": img.select("B6"),
            "S2": img.select("B7"),
            "lambdaG": 560.0,
            "lambdaR": 660.0,
            "lambdaN": 830.0,
        }

    def lookupL45C2(img):
        return {
            "B": img.select("SR_B1"),
            "G": img.select("SR_B2"),
            "R": img.select("SR_B3"),
            "N": img.select("SR_B4"),
            "S1": img.select("SR_B5"),
            "T1": img.select("ST_B6"),
            "S2": img.select("SR_B7"),
            "lambdaG": 560.0,
            "lambdaR": 660.0,
            "lambdaN": 830.0,
        }

    def lookupL7(img):
        return {
            "B": img.select("B1"),
            "G": img.select("B2"),
            "R": img.select("B3"),
            "N": img.select("B4"),
            "S1": img.select("B5"),
            "T1": img.select("B6"),
            "S2": img.select("B7"),
            "lambdaG": 560.0,
            "lambdaR": 660.0,
            "lambdaN": 835.0,
        }

    def lookupL7C2(img):
        return {
            "B": img.select("SR_B1"),
            "G": img.select("SR_B2"),
            "R": img.select("SR_B3"),
            "N": img.select("SR_B4"),
            "S1": img.select("SR_B5"),
            "T1": img.select("ST_B6"),
            "S2": img.select("SR_B7"),
            "lambdaG": 560.0,
            "lambdaR": 660.0,
            "lambdaN": 835.0,
        }

    def lookupMOD09GQ(img):
        return {
            "R": img.select("sur_refl_b01"),
            "N": img.select("sur_refl_b02"),
            "lambdaR": 645.0,
            "lambdaN": 858.5,
        }

    def lookupMOD09GA(img):
        return {
            "B": img.select("sur_refl_b03"),
            "G": img.select("sur_refl_b04"),
            "R": img.select("sur_refl_b01"),
            "N": img.select("sur_refl_b02"),
            "S1": img.select("sur_refl_b06"),
            "S2": img.select("sur_refl_b07"),
            "lambdaG": 555.0,
            "lambdaR": 645.0,
            "lambdaN": 858.5,
        }

    def lookupMCD43A4(img):
        return {
            "B": img.select("Nadir_Reflectance_Band3"),
            "G": img.select("Nadir_Reflectance_Band4"),
            "R": img.select("Nadir_Reflectance_Band1"),
            "N": img.select("Nadir_Reflectance_Band2"),
            "S1": img.select("Nadir_Reflectance_Band6"),
            "S2": img.select("Nadir_Reflectance_Band7"),
            "lambdaG": 555.0,
            "lambdaR": 645.0,
            "lambdaN": 858.5,
        }

    lookupPlatform = {
        "JAXA/ALOS/PALSAR-2/Level2_2/ScanSAR": lookupPALSAR,
        "COPERNICUS/S1_GRD": lookupS1,
        "COPERNICUS/S2": lookupS2,
        "COPERNICUS/S2_HARMONIZED": lookupS2,
        "COPERNICUS/S2_SR": lookupS2,
        "COPERNICUS/S2_SR_HARMONIZED": lookupS2,
        "LANDSAT/LC08/C01/T1_SR": lookupL8,
        "LANDSAT/LC08/C01/T2_SR": lookupL8,
        "LANDSAT/LC08/C02/T1_L2": lookupL8C2,
        "LANDSAT/LC08/C02/T2_L2": lookupL8C2,
        "LANDSAT/LC09/C02/T1_L2": lookupL8C2,
        "LANDSAT/LC09/C02/T2_L2": lookupL8C2,
        "LANDSAT/LE07/C01/T1_SR": lookupL7,
        "LANDSAT/LE07/C01/T2_SR": lookupL7,
        "LANDSAT/LE07/C02/T1_L2": lookupL7C2,
        "LANDSAT/LE07/C02/T2_L2": lookupL7C2,
        "LANDSAT/LT05/C01/T1_SR": lookupL45,
        "LANDSAT/LT05/C01/T2_SR": lookupL45,
        "LANDSAT/LT05/C02/T1_L2": lookupL45C2,
        "LANDSAT/LT05/C02/T2_L2": lookupL45C2,
        "LANDSAT/LT04/C01/T1_SR": lookupL45,
        "LANDSAT/LT04/C01/T2_SR": lookupL45,
        "LANDSAT/LT04/C02/T1_L2": lookupL45C2,
        "LANDSAT/LT04/C02/T2_L2": lookupL45C2,
        "MODIS/006/MOD09GQ": lookupMOD09GQ,
        "MODIS/006/MYD09GQ": lookupMOD09GQ,
        "MODIS/006/MOD09GA": lookupMOD09GA,
        "MODIS/006/MYD09GA": lookupMOD09GA,
        "MODIS/006/MOD09Q1": lookupMOD09GQ,
        "MODIS/006/MYD09Q1": lookupMOD09GQ,
        "MODIS/006/MOD09A1": lookupMOD09GA,
        "MODIS/006/MYD09A1": lookupMOD09GA,
        "MODIS/006/MCD43A4": lookupMCD43A4,
        "MODIS/061/MOD09GQ": lookupMOD09GQ,
        "MODIS/061/MYD09GQ": lookupMOD09GQ,
        "MODIS/061/MOD09GA": lookupMOD09GA,
        "MODIS/061/MYD09GA": lookupMOD09GA,
        "MODIS/061/MOD09Q1": lookupMOD09GQ,
        "MODIS/061/MYD09Q1": lookupMOD09GQ,
        "MODIS/061/MOD09A1": lookupMOD09GA,
        "MODIS/061/MYD09A1": lookupMOD09GA,
        "MODIS/061/MCD43A4": lookupMCD43A4,
    }

    plat = platformDict["platform"]

    if plat not in list(lookupPlatform.keys()):
        raise Exception(
            f"Sorry, satellite platform {plat} not supported for spectral index computation!"
        )

    return lookupPlatform[platformDict["platform"]](img)


def _get_indices(online: bool) -> dict:
    """Retrieves the dictionary of indices used for the index() method in ee.Image and ee.ImageCollection classes.

    Args:
        online : Wheter to retrieve the most recent list of indices directly from the GitHub repository and not from the local copy.

    Returns:
        Indices.
    """
    if online:
        with urllib.request.urlopen(
            "https://raw.githubusercontent.com/awesome-spectral-indices/awesome-spectral-indices/main/output/spectral-indices-dict.json"
        ) as url:
            indices = json.loads(url.read().decode())
    else:
        indices = _load_JSON("spectral-indices-dict.json")

    return indices["SpectralIndices"]


def _get_kernel_image(
    img: ee.Image, lookup: dict, kernel: str, sigma: Union[str, float], a: str, b: str
) -> ee.Image:
    """Creates an ee.Image representing a kernel computed on bands [a] and [b].

    Args:
        img : Image to compute the kernel on.
        lookup : Dictionary retrieved from _get_expression_map().
        kernel : Kernel to use.
        sigma : Length-scale parameter. Used for kernel = 'RBF'.
        a : Key of the first band to use.
        b : Key of the second band to use.

    Returns:
        Kernel image.
    """
    if a not in list(lookup.keys()) or b not in list(lookup.keys()):
        return None
    else:
        lookupab = {"a": lookup[a], "b": lookup[b]}
        if isinstance(sigma, str):
            lookup = {**lookup, **lookupab, "sigma": img.expression(sigma, lookupab)}
        else:
            lookup = {**lookup, **lookupab, "sigma": sigma}
        kernels = {
            "linear": "a * b",
            "RBF": "exp((-1.0 * (a - b) ** 2.0)/(2.0 * sigma ** 2.0))",
            "poly": "((a * b) + c) ** p",
        }
        return img.expression(kernels[kernel], lookup)


def _remove_none_dict(dictionary: dict) -> dict:
    """Removes elements from a dictionary with None values.

    Args:
        dictionary : Dictionary to remove None values.

    Returns:
        Curated dictionary.
    """
    newDictionary = dict(dictionary)
    for key in dictionary.keys():
        if dictionary[key] is None:
            del newDictionary[key]
    return newDictionary


def _get_kernel_parameters(
    img: ee.Image, lookup: dict, kernel: str, sigma: Union[str, float]
) -> dict:
    """Gets the additional kernel parameters to compute kernel indices.

    Args:
        img : Image to compute the kernel parameters on.
        lookup : Dictionary retrieved from _get_expression_map().
        kernel : Kernel to use.
        sigma : Length-scale parameter. Used for kernel = 'RBF'.

    Returns:
        Kernel parameters.
    """
    kernelParameters = {
        "kNN": _get_kernel_image(img, lookup, kernel, sigma, "N", "N"),
        "kNR": _get_kernel_image(img, lookup, kernel, sigma, "N", "R"),
        "kNB": _get_kernel_image(img, lookup, kernel, sigma, "N", "B"),
        "kNL": _get_kernel_image(img, lookup, kernel, sigma, "N", "L"),
        "kGG": _get_kernel_image(img, lookup, kernel, sigma, "G", "G"),
        "kGR": _get_kernel_image(img, lookup, kernel, sigma, "G", "R"),
        "kGB": _get_kernel_image(img, lookup, kernel, sigma, "G", "B"),
        "kBB": _get_kernel_image(img, lookup, kernel, sigma, "B", "B"),
        "kBR": _get_kernel_image(img, lookup, kernel, sigma, "B", "R"),
        "kBL": _get_kernel_image(img, lookup, kernel, sigma, "B", "L"),
        "kRR": _get_kernel_image(img, lookup, kernel, sigma, "R", "R"),
        "kRB": _get_kernel_image(img, lookup, kernel, sigma, "R", "B"),
        "kRL": _get_kernel_image(img, lookup, kernel, sigma, "R", "L"),
        "kLL": _get_kernel_image(img, lookup, kernel, sigma, "L", "L"),
    }

    return kernelParameters


def _get_tc_coefficients(platform: str) -> dict:
    """Gets the platform-specific coefficient dictionary required for tasseled cap
    transformation.

    Platform matching is strict, meaning that data must be at the processing level
    specified by the reference literature that coefficients were sourced from, e.g.
    Landsat 8 SR cannot be transformed with Landsat 8 TOA coefficients.

    Args:
        platform : Platform name retrieved from the STAC.

    Returns:
        Map dictionary with band names and corresponding coefficients for brightness
        greenness, and wetness.

    Raises:
        Exception : If the platform has no supported coefficients.
    """

    SENTINEL2_1C = {
        "bands": (
            "B1",
            "B2",
            "B3",
            "B4",
            "B5",
            "B6",
            "B7",
            "B8",
            "B8A",
            "B9",
            "B10",
            "B11",
            "B12",
        ),
        "TCB": (
            0.2381,
            0.2569,
            0.2934,
            0.3020,
            0.3099,
            0.3740,
            0.4180,
            0.3580,
            0.3834,
            0.0103,
            0.0020,
            0.0896,
            0.0780,
        ),
        "TCG": (
            -0.2266,
            -0.2818,
            -0.3020,
            -0.4283,
            -0.2959,
            0.1602,
            0.3127,
            0.3138,
            0.4261,
            0.1454,
            -0.0017,
            -0.1341,
            -0.2538,
        ),
        "TCW": (
            0.1825,
            0.1763,
            0.1615,
            0.0486,
            0.0170,
            0.0223,
            0.0219,
            -0.0755,
            -0.0910,
            -0.1369,
            0.0003,
            -0.7701,
            -0.5293,
        ),
    }

    # Zhai et al. 2022 also provide coefficients with the blue band, but
    # recommend omitting it due to difficulties in atmospheric correction.
    LANDSAT8_SR = {
        "bands": ("SR_B3", "SR_B4", "SR_B5", "SR_B6", "SR_B7"),
        "TCB": (0.4596, 0.5046, 0.5458, 0.4114, 0.2589),
        "TCG": (-0.3374, -0.4901, 0.7909, 0.0177, -0.1416),
        "TCW": (0.2254, 0.3681, 0.2250, -0.6053, -0.6298)
    }

    # Zhai et al. 2022 coefficients were included for L8 TOA over the Baig 
    # et al. 2014 coefficients for consistency with the L8 SR coefficients, 
    # which were not calculated by Baig et al.
    LANDSAT8_TOA = {
        "bands": ("B3", "B4", "B5", "B6", "B7"),
        "TCB": (0.4321, 0.4971, 0.5695, 0.4192, 0.2569),
        "TCG": (-0.3318, -0.4844, 0.7856, -0.0331, -0.1923),
        "TCW": (0.2633, 0.3945, 0.1801, -0.6121, -0.6066)
    }

    # Coefficients for Landsat 8 OLI are usable for Landsat 9 OLI-2, per
    # Zhai et al. 2022
    LANDSAT9_SR = LANDSAT8_SR
    LANDSAT9_TOA = LANDSAT8_TOA

    LANDSAT7_TOA = {
        "bands": ("B1", "B2", "B3", "B4", "B5", "B7"),
        "TCB": (0.3561, 0.3972, 0.3904, 0.6966, 0.2286, 0.1596),
        "TCG": (-0.3344, -0.3544, -0.4556, 0.6966, -0.0242, -0.2630),
        "TCW": (0.2626, 0.2141, 0.0926, 0.0656, -0.7629, -0.5388),
    }

    LANDSAT4_DN = {
        "bands": ("B1", "B2", "B3", "B4", "B5", "B7"),
        "TCB": (0.3037, 0.2793, 0.4743, 0.5585, 0.5082, 0.1863),
        "TCG": (-0.2848, -0.2435, -0.5435, 0.7243, 0.0840, -0.1800),
        "TCW": (0.1509, 0.1973, 0.3279, 0.3406, -0.7112, -0.4572),
    }

    LANDSAT4_SR = {
        "bands": ("SR_B1", "SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B7"),
        "TCB": (0.2043, 0.4158, 0.5524, 0.5741, 0.3124, 0.2303),
        "TCG": (-0.1603, -0.2819, -0.4934, 0.7940, -0.0002, -0.1446),
        "TCW": (0.0315, 0.2021, 0.3102, 0.1594, -0.6806, -0.6109),
    }

    LANDSAT5_DN = {
        "bands": ("B1", "B2", "B3", "B4", "B5", "B7"),
        "TCB": (0.2909, 0.2493, 0.4806, 0.5568, 0.4438, 0.1706),
        "TCG": (-0.2728, -0.2174, -0.5508, 0.7221, 0.0733, -0.1648),
        "TCW": (0.1446, 0.1761, 0.3322, 0.3396, -0.6210, -0.4186),
    }

    MODIS_NBAR = {
        "bands": (
            "Nadir_Reflectance_Band1",
            "Nadir_Reflectance_Band2",
            "Nadir_Reflectance_Band3",
            "Nadir_Reflectance_Band4",
            "Nadir_Reflectance_Band5",
            "Nadir_Reflectance_Band6",
            "Nadir_Reflectance_Band7",
        ),
        "TCB": (0.4395, 0.5945, 0.2460, 0.3918, 0.3506, 0.2136, 0.2678),
        "TCG": (-0.4064, 0.5129, -0.2744, -0.2893, 0.4882, -0.0036, -0.4169),
        "TCW": (0.1147, 0.2489, 0.2408, 0.3132, -0.3122, -0.6416, -0.5087),
    }

    platformCoeffs = {
        "COPERNICUS/S2": SENTINEL2_1C,
        "MODIS/006/MCD43A4": MODIS_NBAR,
        "LANDSAT/LC09/C02/T1_L2": LANDSAT9_SR,
        "LANDSAT/LC09/C02/T1_TOA": LANDSAT9_TOA,
        "LANDSAT/LC08/C02/T1_L2": LANDSAT8_SR,
        "LANDSAT/LC08/C02/T2_L2": LANDSAT8_SR,
        "LANDSAT/LC08/C01/T1_TOA": LANDSAT8_TOA,
        "LANDSAT/LC08/C01/T1_RT_TOA": LANDSAT8_TOA,
        "LANDSAT/LC08/C01/T2_TOA": LANDSAT8_TOA,
        "LANDSAT/LE07/C01/T1_TOA": LANDSAT7_TOA,
        "LANDSAT/LE07/C01/T1_RT_TOA": LANDSAT7_TOA,
        "LANDSAT/LE07/C01/T2_TOA": LANDSAT7_TOA,
        "LANDSAT/LT05/C01/T1": LANDSAT5_DN,
        "LANDSAT/LT05/C01/T2": LANDSAT5_DN,
        "LANDSAT/LT04/C02/T1_L2": LANDSAT4_SR,
        "LANDSAT/LT04/C02/T2_L2": LANDSAT4_SR,
        "LANDSAT/LT04/C01/T1": LANDSAT4_DN,
        "LANDSAT/LT04/C01/T2": LANDSAT4_DN,
    }


    if platform not in list(platformCoeffs.keys()):
        raise Exception(
            "Sorry, satellite platform not supported for tasseled cap transformation! Use one of "
            + str(list(platformCoeffs.keys()))
        )

    return platformCoeffs[platform]


def _match_histogram(
    source: ee.Image,
    target: ee.Image,
    bands: Optional[Dict[str, str]],
    geometry: Optional[ee.Geometry],
    maxBuckets: int,
) -> ee.Image:
    """Adjust the histogram of an image to match a target image.

    Args:
        source : Image to adjust.
        target : Image to use as the histogram reference.
        bands : An optional dictionary of band names to match, with source bands as keys
            and target bands as values. If none is provided, bands will be matched by name.
            Any bands not included here will be dropped.
        geometry : The optional region to match histograms in that overlaps both images.
            If none is provided, the geometry of the source image will be used. If the
            source image is unbounded and no geometry is provided, histogram matching will
            fail.
        maxBuckets : The maximum number of buckets to use when building histograms. More
            buckets will require more memory and time but will generate more accurate
            results. The number of buckets will be rounded to the nearest power of 2.

    Returns:
        The adjusted image containing the matched source bands.
    """

    def histogram_lookup(
        source_hist: ee.Array, target_hist: ee.Array
    ) -> Tuple[ee.List, ee.List]:
        """Build a list of target values with corresponding counts to source values from a source and target histogram.

        Args:
            source_hist : A histogram for a source image returned by ee.Reducer.autoHistogram
            target_hist : A histogram for a target image returned by ee.Reducer.autoHistogram

        Returns:
            Source histogram values and target histogram values with corresponding counts.
        """
        source_vals = source_hist.slice(1, 0, 1).project([0])
        source_counts = source_hist.slice(1, 1, 2).project([0])
        source_counts = source_counts.divide(source_counts.get([-1]))

        target_vals = target_hist.slice(1, 0, 1).project([0])
        target_counts = target_hist.slice(1, 1, 2).project([0])
        target_counts = target_counts.divide(target_counts.get([-1]))

        def lookup_value(n):
            """Find the first target value with at least n counts."""
            index = target_counts.gte(n).argmax()
            return target_vals.get(index)

        target_lookup_vals = source_counts.toList().map(lookup_value)

        return (source_vals.toList(), target_lookup_vals)

    geometry = ee.Element.geometry(source) if geometry is None else geometry

    source_bands = source.bandNames() if bands is None else list(bands.keys())
    target_bands = source.bandNames() if bands is None else list(bands.values())
    bands = ee.Dictionary.fromLists(source_bands, target_bands)

    source = source.select(source_bands)
    target = target.select(target_bands)

    source_histogram = source.reduceRegion(
        reducer=ee.Reducer.autoHistogram(maxBuckets=maxBuckets, cumulative=True),
        geometry=geometry,
        scale=30,
        maxPixels=1e13,
        bestEffort=True,
    )

    target_histogram = target.updateMask(source.mask()).reduceRegion(
        reducer=ee.Reducer.autoHistogram(maxBuckets=maxBuckets, cumulative=True),
        geometry=geometry,
        scale=30,
        maxPixels=1e13,
        bestEffort=True,
    )

    def match_bands(source_band: ee.String, target_band: ee.String) -> ee.Image:
        """Match the histogram of one source band to a target band.

        Args:
            source_band : The name of a band in the source image to adjust.
            target_band : The name of a corresponding band in the target image to match to.

        Returns:
            The source band image histogram-matched to the target band.
        """
        x, y = histogram_lookup(
            source_histogram.getArray(source_band),
            target_histogram.getArray(target_band),
        )
        matched = source.select([source_band]).interpolate(x, y)
        return matched

    matched = (
        ee.ImageCollection(bands.map(match_bands).values())
        .toBands()
        .rename(bands.keys())
    )

    # Preserve the metadata, band types, and band order of the source image.
    matched = ee.Image(matched.copyProperties(source, source.propertyNames()))
    matched = matched.cast(source.bandTypes(), source.bandNames())
    matched = matched.set("ee_extra:HISTOGRAM_TARGET", target)

    # If the source image was bounded, clip the matched output to its bounds. If the source
    # image doesn't have a `geometry` this will fail, but that seems exceptionally rare.
    matched = ee.Algorithms.If(
        source.geometry().isUnbounded(),
        matched,
        matched.clip(source.geometry().bounds()),
    )

    return ee.Image(matched)
