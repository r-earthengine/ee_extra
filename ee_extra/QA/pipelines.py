from typing import Union

import ee

from ee_extra.QA.clouds import maskClouds
from ee_extra.STAC.core import scaleAndOffset


def preprocess(
    x: Union[ee.Image, ee.ImageCollection], **kwargs
) -> Union[ee.Image, ee.ImageCollection]:
    """Pre-process the image, or image collection: masks clouds and shadows, and scales and offsets the image, or image collection.

    Parameters:
        x : Image or Image Collection to pre-process.
        **kwargs : Keywords arguments for maskClouds().

    Returns:
        Pre-processed image or image collection.
    """
    maskCloudsDefault = {
        "method": "cloud_prob",
        "prob": 60,
        "maskCirrus": True,
        "maskShadows": True,
        "scaledImage": False,
        "dark": 0.15,
        "cloudDist": 1000,
        "buffer": 250,
        "cdi": None,
    }

    for key, value in maskCloudsDefault.items():
        if key not in kwargs.keys():
            kwargs[key] = value

    x = maskClouds(x, **kwargs)
    x = scaleAndOffset(x)

    return x
