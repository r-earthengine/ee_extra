import json
import os
import re
import urllib.request
import warnings
from typing import Optional, Union

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
            "RE4": img.select("B8A"),
            "WV": img.select("B9"),
            "S1": img.select("B11"),
            "S2": img.select("B12"),
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
        }

    def lookupL457(img):
        return {
            "B": img.select("B1"),
            "G": img.select("B2"),
            "R": img.select("B3"),
            "N": img.select("B4"),
            "S1": img.select("B5"),
            "T1": img.select("B6"),
            "S2": img.select("B7"),
        }

    def lookupL457C2(img):
        return {
            "B": img.select("SR_B1"),
            "G": img.select("SR_B2"),
            "R": img.select("SR_B3"),
            "N": img.select("SR_B4"),
            "S1": img.select("SR_B5"),
            "T1": img.select("ST_B6"),
            "S2": img.select("SR_B7"),
        }

    def lookupMOD09GQ(img):
        return {"R": img.select("sur_refl_b01"), "N": img.select("sur_refl_b02")}

    def lookupMOD09GA(img):
        return {
            "B": img.select("sur_refl_b03"),
            "G": img.select("sur_refl_b04"),
            "R": img.select("sur_refl_b01"),
            "N": img.select("sur_refl_b02"),
            "S1": img.select("sur_refl_b06"),
            "S2": img.select("sur_refl_b07"),
        }

    def lookupMCD43A4(img):
        return {
            "B": img.select("Nadir_Reflectance_Band3"),
            "G": img.select("Nadir_Reflectance_Band4"),
            "R": img.select("Nadir_Reflectance_Band1"),
            "N": img.select("Nadir_Reflectance_Band2"),
            "S1": img.select("Nadir_Reflectance_Band6"),
            "S2": img.select("Nadir_Reflectance_Band7"),
        }

    lookupPlatform = {
        "COPERNICUS/S2": lookupS2,
        "COPERNICUS/S2_SR": lookupS2,
        "LANDSAT/LC08/C01/T1_SR": lookupL8,
        "LANDSAT/LC08/C01/T2_SR": lookupL8,
        "LANDSAT/LC08/C02/T1_L2": lookupL8C2,
        "LANDSAT/LE07/C01/T1_SR": lookupL457,
        "LANDSAT/LE07/C01/T2_SR": lookupL457,
        "LANDSAT/LE07/C02/T1_L2": lookupL457C2,
        "LANDSAT/LT05/C01/T1_SR": lookupL457,
        "LANDSAT/LT05/C01/T2_SR": lookupL457,
        "LANDSAT/LT05/C02/T1_L2": lookupL457C2,
        "LANDSAT/LT04/C01/T1_SR": lookupL457,
        "LANDSAT/LT04/C01/T2_SR": lookupL457,
        "LANDSAT/LT04/C02/T1_L2": lookupL457C2,
        "MODIS/006/MOD09GQ": lookupMOD09GQ,
        "MODIS/006/MYD09GQ": lookupMOD09GQ,
        "MODIS/006/MOD09GA": lookupMOD09GA,
        "MODIS/006/MYD09GA": lookupMOD09GA,
        "MODIS/006/MOD09Q1": lookupMOD09GQ,
        "MODIS/006/MYD09Q1": lookupMOD09GQ,
        "MODIS/006/MOD09A1": lookupMOD09GA,
        "MODIS/006/MYD09A1": lookupMOD09GA,
        "MODIS/006/MCD43A4": lookupMCD43A4,
    }

    if platformDict["platform"] not in list(lookupPlatform.keys()):
        raise Exception(
            "Sorry, satellite platform not supported for index computation!"
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
            "https://raw.githubusercontent.com/davemlz/awesome-ee-spectral-indices/main/output/spectral-indices-dict.json"
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


def _get_tc_coefficients(platformDict: dict) -> dict:
    """Gets the platform-specific coefficient dictionary required for tasseled cap
    transformation.

    Platform matching is strict, meaning that data must be at the processing level
    specified by the reference literature that coefficients were sourced from, e.g.
    Landsat 8 SR cannot be transformed with Landsat 8 TOA coefficients.

    Coefficients are provided for the following platforms:

    * Sentinel-2 MSI Level 1C [1]_
    * Landsat 8 OLI TOA [2]_
    * Landsat 7 ETM+ TOA [3]_
    * Landsat 5 TM Raw DN [4]_
    * Landsat 4 TM Raw DN [5]_
    * Landsat 4 TM Surface Reflectance [6]_
    * MODIS NBAR [7]_

    Args:
        platformDict : Dictionary retrieved from the _get_STAC_platform() method.

    Returns:
        Map dictionary with band names and corresponding coefficients for brightness
        greenness, and wetness.

    Raises:
        Exception : If the platform has no supported coefficients.

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

    LANDSAT8_TOA = {
        "bands": ("B2", "B3", "B4", "B5", "B6", "B7"),
        "TCB": (0.3029, 0.2786, 0.4733, 0.5599, 0.5080, 0.1872),
        "TCG": (-0.2941, -0.2430, -0.5424, 0.7276, 0.0713, -0.1608),
        "TCW": (0.1511, 0.1973, 0.3283, 0.3407, -0.7117, -0.4559),
    }

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

    platform = platformDict["platform"]

    if platform not in list(platformCoeffs.keys()):
        raise Exception(
            "Sorry, satellite platform not supported for tasseled cap transformation! Use one of "
            + str(list(platformCoeffs.keys()))
        )

    return platformCoeffs[platform]
