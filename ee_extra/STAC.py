import ee
import json
import pkg_resources
import os
import warnings
import requests
import re
from typing import Optional, Union


warnings.simplefilter("always", UserWarning)


def _get_platform_STAC(args: Union[ee.Image, ee.ImageCollection]) -> dict:
    """Gets the platform (satellite) of an image (or image collection) and wheter if it is a Surface Reflectance product.

    Args:    
        args : An Image or Image Collection to get the platform from.

    Returns:    
        Platform and product of the Image (or Image Collection).
    """
    eeExtraDir = os.path.dirname(pkg_resources.resource_filename("ee_extra", "ee_extra.py"))
    dataPath = os.path.join(eeExtraDir, "data/ee-catalog-ids.json")

    f = open(dataPath)
    eeDict = json.load(f)
    platforms = list(eeDict.keys())

    ID = args.get("system:id").getInfo()

    plt = None

    for platform in platforms:

        if eeDict[platform]["gee:type"] == "image_collection" and isinstance(
            args, ee.image.Image
        ):
            pltID = "/".join(ID.split("/")[:-1])
        elif eeDict[platform]["gee:type"] == "image" and isinstance(
            args, ee.imagecollection.ImageCollection
        ):
            pass
        else:
            pltID = ID

        if platform == pltID:
            plt = pltID

        if "_SR" in pltID:
            platformDict = {"platform": plt, "sr": True}
        else:
            platformDict = {"platform": plt, "sr": False}

    if plt is None:
        raise Exception("Sorry, satellite platform not supported!")

    return platformDict


def getSTAC(x: Union[ee.Image, ee.ImageCollection]) -> dict:
    """Gets the STAC of the specified platform.

    Args:    
        x : Image or image collection to get the STAC from.

    Returns:    
        STAC of the ee.Image or ee.ImageCollection dataset.
        
    Examples:
        >>> import ee
        >>> from ee_extra.STAC import getSTAC
        >>> ee.Initialize()
        >>> S2 = ee.ImageCollection("COPERNICUS/S2_SR")
        >>> getSTAC(S2)
    """
    platformDict = _get_platform_STAC(x)

    eeExtraDir = os.path.dirname(pkg_resources.resource_filename("ee_extra", "ee_extra.py"))
    dataPath = os.path.join(eeExtraDir, "data/ee-catalog-ids.json")

    f = open(dataPath)
    eeDict = json.load(f)

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
        >>> from ee_extra.STAC import getScaleParams
        >>> ee.Initialize()
        >>> S2 = ee.ImageCollection("COPERNICUS/S2_SR")
        >>> getScaleParams(S2)
    """
    platformDict = _get_platform_STAC(x)

    eeExtraDir = os.path.dirname(pkg_resources.resource_filename("ee_extra", "ee_extra.py"))
    dataPath = os.path.join(eeExtraDir, "data/ee-catalog-scale.json")

    f = open(dataPath)
    eeDict = json.load(f)
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
        >>> from ee_extra.STAC import getOffsetParams
        >>> ee.Initialize()
        >>> S2 = ee.ImageCollection("COPERNICUS/S2_SR")
        >>> getOffsetParams(S2)
    """
    platformDict = _get_platform_STAC(x)

    eeExtraDir = os.path.dirname(pkg_resources.resource_filename("ee_extra", "ee_extra.py"))
    dataPath = os.path.join(eeExtraDir, "data/ee-catalog-offset.json")

    f = open(dataPath)
    eeDict = json.load(f)
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
        >>> from ee_extra.STAC import scaleAndOffset
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
        >>> from ee_extra.STAC import getDOI
        >>> ee.Initialize()
        >>> S2 = ee.ImageCollection("COPERNICUS/S2_SR")
        >>> getDOI(S2)
    """
    platformDict = _get_platform_STAC(x)

    eeExtraDir = os.path.dirname(pkg_resources.resource_filename("ee_extra", "ee_extra.py"))
    dataPath = os.path.join(eeExtraDir, "data/ee-catalog-ids.json")

    f = open(dataPath)
    eeDict = json.load(f)

    return eeDict[platformDict["platform"]]["sci:doi"]


def getCitation(x: Union[ee.Image, ee.ImageCollection]) -> str:
    """Gets the citation of the specified platform, if available.

    Args:
        x : Image or Image Collection to get the citation from.

    Returns:
        Citation of the ee.Image or ee.ImageCollection dataset.
        
    Examples:
        >>> import ee
        >>> from ee_extra.STAC import getCitation
        >>> ee.Initialize()
        >>> S2 = ee.ImageCollection("COPERNICUS/S2_SR")
        >>> getCitation(S2)
    """
    platformDict = _get_platform_STAC(x)

    eeExtraDir = os.path.dirname(pkg_resources.resource_filename("ee_extra", "ee_extra.py"))
    dataPath = os.path.join(eeExtraDir, "data/ee-catalog-ids.json")

    f = open(dataPath)
    eeDict = json.load(f)

    return eeDict[platformDict["platform"]]["sci:citation"]