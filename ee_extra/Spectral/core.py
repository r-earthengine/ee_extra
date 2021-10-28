import json
import os
import re
import warnings
from typing import Any, List, Optional, Union

import ee
import requests

from ee_extra.Spectral.utils import (
    _get_expression_map,
    _get_indices,
    _get_kernel_image,
    _get_kernel_parameters,
    _get_tc_coefficients,
    _remove_none_dict,
)
from ee_extra.STAC.utils import _get_platform_STAC


def spectralIndices(
    x: Union[ee.Image, ee.ImageCollection],
    index: Union[str, List[str]] = "NDVI",
    G: Union[float, int] = 2.5,
    C1: Union[float, int] = 6.0,
    C2: Union[float, int] = 7.5,
    L: Union[float, int] = 1.0,
    cexp: Union[float, int] = 1.16,
    nexp: Union[float, int] = 2.0,
    alpha: Union[float, int] = 0.1,
    slope: Union[float, int] = 1.0,
    intercept: Union[float, int] = 0.0,
    gamma: Union[float, int] = 1.0,
    kernel: str = "RBF",
    sigma: Union[float, str] = "0.5 * (a + b)",
    p: Union[float, int] = 2,
    c: Union[float, int] = 1.0,
    online: bool = False,
) -> Union[ee.Image, ee.ImageCollection]:
    """Computes one or more spectral indices (indices are added as bands) for an image oir image collection.

    Args:
        x : Image or Image Collectionto compute indices on. Must be scaled to [0,1].
        index : Index or list of indices to compute.
        G : Gain factor. Used just for index = 'EVI'.
        C1 : Coefficient 1 for the aerosol resistance term. Used just for index = 'EVI'.
        C2 : Coefficient 2 for the aerosol resistance term. Used just for index = 'EVI'.
        L : Canopy background adjustment. Used just for index = ['EVI','SAVI'].
        cexp : Exponent used for OCVI.
        nexp : Exponent used for GDVI.
        alpha : Weighting coefficient  used for WDRVI.
        slope : Soil line slope.
        intercept : Soil line intercept.
        gamma : Weighting coefficient  used for ARVI.
        kernel : Kernel used for kernel indices. One of 'linear', 'RBF', 'poly'.
        sigma : Length-scale parameter. Used for kernel = 'RBF'. If str, this must be an expression including 'a' and 'b'. If numeric, this must be positive.
        p : Kernel degree. Used for kernel = 'poly'.
        c : Free parameter that trades off the influence of higher-order versus lower-order terms. Used for kernel = 'poly'. This must be greater than or equal to 0.
        online : Wheter to retrieve the most recent list of indices directly from the GitHub repository and not from the local copy.

    Returns:
        Image or Image Collection with the computed spectral index, or indices, as new bands.

    Examples:
        >>> import ee
        >>> from ee_extra.Spectral.core import spectralIndices
        >>> ee.Initialize()
        >>> S2 = ee.ImageCollection("COPERNICUS/S2_SR")
        >>> spectralIndices(S2,["NDVI","SAVI"],L = 0.5)
    """
    platformDict = _get_platform_STAC(x)

    if isinstance(sigma, int) or isinstance(sigma, float):
        if sigma < 0:
            raise Exception(f"[sigma] must be positive! Value passed: sigma = {sigma}")

    if p <= 0 or c < 0:
        raise Exception(
            f"[p] and [c] must be positive! Values passed: p = {p}, c = {c}"
        )

    additionalParameters = {
        "g": float(G),
        "C1": float(C1),
        "C2": float(C2),
        "L": float(L),
        "cexp": float(cexp),
        "nexp": float(nexp),
        "alpha": float(alpha),
        "sla": float(slope),
        "slb": float(intercept),
        "gamma": float(gamma),
        "p": float(p),
        "c": float(c),
    }

    spectralIndices = _get_indices(online)
    indicesNames = list(spectralIndices.keys())

    if not isinstance(index, list):
        if index == "all":
            index = list(spectralIndices.keys())
        elif index in [
            "vegetation",
            "burn",
            "water",
            "snow",
            "drought",
            "urban",
            "kernel",
        ]:
            temporalListOfIndices = []
            for idx in indicesNames:
                if spectralIndices[idx]["type"] == index:
                    temporalListOfIndices.append(idx)
            index = temporalListOfIndices
        else:
            index = [index]

    for idx in index:
        if idx not in list(spectralIndices.keys()):
            warnings.warn(
                f"Index {idx} is not a built-in index and it won't be computed!"
            )
        else:

            def temporalIndex(img):
                lookupDic = _get_expression_map(img, platformDict)
                lookupDic = {**lookupDic, **additionalParameters}
                kernelParameters = _get_kernel_parameters(img, lookupDic, kernel, sigma)
                lookupDic = {**lookupDic, **kernelParameters}
                lookupDicCurated = _remove_none_dict(lookupDic)
                if all(
                    band in list(lookupDicCurated.keys())
                    for band in spectralIndices[idx]["bands"]
                ):
                    return img.addBands(
                        img.expression(
                            spectralIndices[idx]["formula"], lookupDicCurated
                        ).rename(idx)
                    )
                else:
                    warnings.warn(
                        f"This platform doesn't have the required bands for {idx} computation!"
                    )
                    return img

            if isinstance(x, ee.imagecollection.ImageCollection):
                x = x.map(temporalIndex)
            elif isinstance(x, ee.image.Image):
                x = temporalIndex(x)

    return x


def indices(online: bool = False) -> dict:
    """Gets the dictionary of available indices.

    Args:
        online : Whether to retrieve the most recent list of indices directly from the GitHub repository and not from the local copy.

    Returns:
        Dictionary of available indices.

    Examples:
        >>> import ee
        >>> from ee_extra.Spectral.core import indices
        >>> ee.Initialize()
        >>> ind = indices()
        >>> ind.BAIS2.long_name
        'Burned Area Index for Sentinel 2'
        >>> ind.BAIS2.formula
        '(1.0 - ((RE2 * RE3 * RE4) / R) ** 0.5) * (((S2 - RE4)/(S2 + RE4) ** 0.5) + 1.0)'
        >>> ind.BAIS2.reference
        'https://doi.org/10.3390/ecrs-2-05177'
    """
    return _get_indices(online)


def listIndices(online: bool = False) -> list:
    """Gets the list of available indices.

    Args:
        online : Whether to retrieve the most recent list of indices directly from the GitHub repository and not from the local copy.

    Returns:
        List of available indices.

    Examples:
        >>> import ee
        >>> from ee_extra.Spectral.core import listIndices
        >>> ee.Initialize()
        >>> listIndices()
        ['BNDVI','CIG','CVI','EVI','EVI2','GBNDVI','GNDVI',...]
    """
    return list(_get_indices(online).keys())


def tasseledCap(
    x: Union[ee.Image, ee.ImageCollection]
) -> Union[ee.Image, ee.ImageCollection]:
    """Calculates tasseled cap brightness, wetness, and greenness components for an image
    or image collection.

    Tasseled cap transformations are applied using coefficients published for these
    supported platforms:

    * Sentinel-2 MSI Level 1C [1]_
    * Landsat 8 OLI TOA [2]_
    * Landsat 7 ETM+ TOA [3]_
    * Landsat 5 TM Raw DN [4]_
    * Landsat 4 TM Raw DN [5]_
    * Landsat 4 TM Surface Reflectance [6]_
    * MODIS NBAR [7]_

    Args:
        x : Image or Image Collection to calculate tasseled cap components for. Must
            belong to a supported platform.

    Returns:
        Image or Image Collection with the tasseled cap components as new bands.

    References:
        .. [1] Shi, T., & Xu, H. (2019). Derivation of Tasseled Cap Transformation
           Coefficients for Sentinel-2 MSI At-Sensor Reflectance Data. IEEE Journal
           of Selected Topics in Applied Earth Observations and Remote Sensing, 1–11.
           doi:10.1109/jstars.2019.2938388
        .. [2] Baig, M.H.A., Zhang, L., Shuai, T. and Tong, Q., 2014. Derivation of a
           tasselled cap transformation based on Landsat 8 at-satellite reflectance.
           Remote Sensing Letters, 5(5), pp.423-431.
        .. [3] Huang, C., Wylie, B., Yang, L., Homer, C. and Zylstra, G., 2002.
           Derivation of a tasselled cap transformation based on Landsat 7 at-satellite
           reflectance. International journal of remote sensing, 23(8), pp.1741-1748.
        .. [4] Crist, E.P., Laurin, R. and Cicone, R.C., 1986, September. Vegetation and
           soils information contained in transformed Thematic Mapper data. In
           Proceedings of IGARSS’86 symposium (pp. 1465-1470). Paris: European Space
           Agency Publications Division.
        .. [5] Crist, E.P. and Cicone, R.C., 1984. A physically-based transformation of
           Thematic Mapper data---The TM Tasseled Cap. IEEE Transactions on Geoscience
           and Remote sensing, (3), pp.256-263.
        .. [6] Crist, E.P., 1985. A TM tasseled cap equivalent transformation for
           reflectance factor data. Remote sensing of Environment, 17(3), pp.301-306.
        .. [7] Lobser, S.E. and Cohen, W.B., 2007. MODIS tasselled cap: land cover
           characteristics expressed through transformed MODIS data. International
           Journal of Remote Sensing, 28(22), pp.5079-5101.

    Examples:
        >>> import ee
        >>> from ee_extra.Spectral.core import tasseledCap
        >>> ee.Initialize()
        >>> img = ee.Image("LANDSAT/LT05/C01/T1/LT05_044034_20081011")
        >>> img = tasseledCap(img)
    """
    platformDict = _get_platform_STAC(x)
    coeffs = _get_tc_coefficients(platformDict)

    def calculateAndAddComponents(img: ee.Image) -> ee.Image:
        """Calculates tasseled cap components for a single image and adds them as new bands."""
        img = img.select(coeffs["bands"])
        components = [
            img.multiply(coeffs[comp]).reduce(ee.Reducer.sum()).rename(comp)
            for comp in ["TCB", "TCG", "TCW"]
        ]
        return img.addBands(components)

    if isinstance(x, ee.ImageCollection):
        x = x.map(calculateAndAddComponents)
    elif isinstance(x, ee.Image):
        x = calculateAndAddComponents(x)

    return x
