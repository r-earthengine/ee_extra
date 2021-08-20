import json
import os
import re
import warnings
from typing import Optional, Union

import ee
import pkg_resources
import requests

from ee_extra.utils import _load_JSON


def _get_platform_STAC(args: Union[ee.Image, ee.ImageCollection]) -> dict:
    """Gets the platform (satellite) of an image (or image collection) and wheter if it is a Surface Reflectance product.

    Args:
        args : An Image or Image Collection to get the platform from.

    Returns:
        Platform and product of the Image (or Image Collection).
    """
    eeDict = _load_JSON()
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
