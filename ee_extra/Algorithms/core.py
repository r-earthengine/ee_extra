from typing import Any, TypeVar

import ee

from ee_extra.Algorithms.panSharpening import _panSharpen

ImageLike = TypeVar("ImageLike", ee.Image, ee.ImageCollection)


def panSharpen(img: ImageLike, method: str = "SFIM", **kwargs: Any) -> ImageLike:
    """Apply panchromatic sharpening to an Image or ImageCollection.

    Args:
        img : Image or ImageCollection to sharpen.
        method : The sharpening algorithm to apply. Current options are "SFIM" (Smoothing
            Filter-based Intensity Modulation), "HPFA" (High Pass Filter Addition), "PCS"
            (Principal Component Substitution), and "SM" (simple mean).
        kwargs : Keyword arguments passed to ee.Image.reduceRegion() such as "geometry",
            "maxPixels", "bestEffort", etc. These arguments are only used for PCS sharpening
            and quality assessments.

    Returns:
        The Image with all sharpenable bands sharpened to the panchromatic resolution.

    Examples:
    >>> import ee
    >>> from ee_extra.Algorithms.core import panSharpen
    >>> ee.Initialize()
    >>> img = ee.Image("LANDSAT/LC08/C01/T1_TOA/LC08_047027_20160819")
    >>> sharp = panSharpen(img, method="HPFA", maxPixels=1e13)
    """
    return _panSharpen(img, method, **kwargs)
