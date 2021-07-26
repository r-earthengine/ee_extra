from typing import Optional, Union

import json
import os
import re
import warnings

import ee
import pkg_resources
import requests
from ee_extra.STAC.utils import _get_platform_STAC
from ee_extra.utils import _load_JSON


def getSTAC(x: Union[ee.Image, ee.ImageCollection]) -> dict:
    """Gets the STAC of the specified platform.

    Args:
        x : Image or image collection to get the STAC from.

    Returns:
        STAC of the ee.Image or ee.ImageCollection dataset.

    Examples:
        >>> import ee
        >>> from ee_extra.STAC.core import getSTAC
        >>> ee.Initialize()
        >>> S2 = ee.ImageCollection("COPERNICUS/S2_SR")
        >>> getSTAC(S2)
    """
    platformDict = _get_platform_STAC(x)
    eeDict = _load_JSON()
    STAC = requests.get(eeDict[platformDict["platform"]]["href"]).json()

    return STAC


def getScaleParams(x: Union[ee.Image, ee.ImageCollection]) -> dict:
    """Gets the scale parameters for each band of the image or image collection.

    Args:
        x : Image or image collection to get the scale parameters from.

    Returns:
        Dictionary with the scale parameters for each band.

    Examples:
        >>> import ee
        >>> from ee_extra.STAC.core import getScaleParams
        >>> ee.Initialize()
        >>> S2 = ee.ImageCollection("COPERNICUS/S2_SR")
        >>> getScaleParams(S2)
    """
    platformDict = _get_platform_STAC(x)
    eeDict = _load_JSON("ee-catalog-scale.json")
    platforms = list(eeDict.keys())

    if platformDict["platform"] not in platforms:
        warnings.warn("This platform is not supported for getting scale parameters.")
        return None
    else:
        return eeDict[platformDict["platform"]]


def getOffsetParams(x: Union[ee.Image, ee.ImageCollection]) -> dict:
    """Gets the offset parameters for each band of the image or image collection.

    Args:
        x : Image or image collection to get the offset parameters from.

    Returns:
        Dictionary with the offset parameters for each band.

    Examples:
        >>> import ee
        >>> from ee_extra.STAC.core import getOffsetParams
        >>> ee.Initialize()
        >>> S2 = ee.ImageCollection("COPERNICUS/S2_SR")
        >>> getOffsetParams(S2)
    """
    platformDict = _get_platform_STAC(x)
    eeDict = _load_JSON("ee-catalog-offset.json")
    platforms = list(eeDict.keys())

    if platformDict["platform"] not in platforms:
        warnings.warn("This platform is not supported for getting offset parameters.")
        return None
    else:
        return eeDict[platformDict["platform"]]


def scaleAndOffset(x: Union[ee.Image, ee.ImageCollection]) -> Union[ee.Image, ee.ImageCollection]:
    """Scales and offsets bands on an Image or Image Collection.

    Args:
        x : Image or Image Collection to scale.

    Returns:
        Scaled image or image collection.

    Examples:
        >>> import ee
        >>> from ee_extra.STAC.core import scaleAndOffset
        >>> ee.Initialize()
        >>> S2 = ee.ImageCollection("COPERNICUS/S2_SR")
        >>> scaleAndOffset(S2)
    """
    scaleParams = getScaleParams(x)
    offsetParams = getOffsetParams(x)

    if scaleParams is None or offsetParams is None:
        warnings.warn("This platform is not supported for scaling and offsetting.")
        return x
    else:
        scaleParams = ee.Dictionary(scaleParams).toImage()
        offsetParams = ee.Dictionary(offsetParams).toImage()

        def scaleOffset(img):
            bands = img.bandNames()
            scaleList = scaleParams.bandNames()
            bands = bands.filter(ee.Filter.inList("item", scaleList))
            SOscaleParams = scaleParams.select(bands)
            SOoffsetParams = offsetParams.select(bands)
            scaled = img.select(bands).multiply(SOscaleParams).add(SOoffsetParams)
            return ee.Image(scaled.copyProperties(img, img.propertyNames()))

        if isinstance(x, ee.image.Image):
            scaled = scaleOffset(x)
        elif isinstance(x, ee.imagecollection.ImageCollection):
            scaled = x.map(scaleOffset)

        return scaled


def getDOI(x: Union[ee.Image, ee.ImageCollection]) -> str:
    """Gets the DOI of the specified platform, if available.

    Args:
        x : Image or Image Collection to get the DOI from.

    Returns:
        DOI of the ee.Image or ee.ImageCollection dataset.

    Examples:
        >>> import ee
        >>> from ee_extra.STAC.core import getDOI
        >>> ee.Initialize()
        >>> S2 = ee.ImageCollection("COPERNICUS/S2_SR")
        >>> getDOI(S2)
    """
    platformDict = _get_platform_STAC(x)
    eeDict = _load_JSON()

    return eeDict[platformDict["platform"]]["sci:doi"]


def getCitation(x: Union[ee.Image, ee.ImageCollection]) -> str:
    """Gets the citation of the specified platform, if available.

    Args:
        x : Image or Image Collection to get the citation from.

    Returns:
        Citation of the ee.Image or ee.ImageCollection dataset.

    Examples:
        >>> import ee
        >>> from ee_extra.STAC.core import getCitation
        >>> ee.Initialize()
        >>> S2 = ee.ImageCollection("COPERNICUS/S2_SR")
        >>> getCitation(S2)
    """
    platformDict = _get_platform_STAC(x)
    eeDict = _load_JSON()

    return eeDict[platformDict["platform"]]["sci:citation"]


def listDatasets() -> list:
    """Returns all datasets from the GEE STAC as a list.

    Returns:
        List of all datasets from the GEE STAC.

    Examples:
        >>> import ee
        >>> from ee_extra.STAC.core import listDatasets
        >>> ee.Initialize()
        >>> listDatasets()
    """    
    eeDict = _load_JSON()

    return list(eeDict.keys())
