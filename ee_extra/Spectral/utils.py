import json
import os
import re
import warnings
from typing import Optional, Union

import ee
import pkg_resources
import requests

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

    def lookupL7C2(img):
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
        "LANDSAT/LE07/C02/T1_L2": lookupL7C2,
        "LANDSAT/LT05/C01/T1_SR": lookupL457,
        "LANDSAT/LT05/C01/T2_SR": lookupL457,
        "LANDSAT/LT04/C01/T1_SR": lookupL457,
        "LANDSAT/LT04/C01/T2_SR": lookupL457,
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
        indices = requests.get(
            "https://raw.githubusercontent.com/davemlz/awesome-ee-spectral-indices/main/output/spectral-indices-dict.json"
        ).json()
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
