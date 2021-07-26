import ee
import json
import pkg_resources
import os
import warnings
import requests
import re
from typing import Optional, Union
from ee_extra.STAC.utils import _get_platform_STAC


def closest(
    x: ee.ImageCollection,
    date: Union[ee.Date, str],
    tolerance: Union[float, int] = 1,
    unit: str = "month",
) -> ee.ImageCollection:
    """Gets the closest image (or set of images if the collection intersects a region that requires multiple scenes) to the specified date.

    Args:
        x : Image Collection from which to get the closest image to the specified date.
        date : Date of interest. The method will look for images closest to this date.
        tolerance : Filter the collection to [date - tolerance, date + tolerance) before searching the closest image.
            This speeds up the searching process for collections with a high temporal resolution.
        unit : Units for tolerance. Available units: 'year', 'month', 'week', 'day', 'hour', 'minute' or 'second'.

    Returns:
        Closest images to the specified date.

    Examples:
        >>> import ee
        >>> from ee_extra.ImageCollection.core import closest
        >>> ee.Initialize()
        >>> S2 = ee.ImageCollection('COPERNICUS/S2_SR')
        >>> closest(S2,'2018-01-23')
    """
    if not isinstance(date, ee.ee_date.Date):
        date = ee.Date(date)

    startDate = date.advance(-tolerance, unit)
    endDate = date.advance(tolerance, unit)
    x = x.filterDate(startDate, endDate)

    def setProperties(img):
        img = img.set(
            "dateDist",
            ee.Number(img.get("system:time_start")).subtract(date.millis()).abs(),
        )
        img = img.set("day", ee.Date(img.get("system:time_start")).get("day"))
        img = img.set("month", ee.Date(img.get("system:time_start")).get("month"))
        img = img.set("year", ee.Date(img.get("system:time_start")).get("year"))
        return img

    x = x.map(setProperties).sort("dateDist")
    closestImageTime = x.limit(1).first().get("system:time_start")
    dayToFilter = ee.Filter.eq("day", ee.Date(closestImageTime).get("day"))
    monthToFilter = ee.Filter.eq("month", ee.Date(closestImageTime).get("month"))
    yearToFilter = ee.Filter.eq("year", ee.Date(closestImageTime).get("year"))
    x = x.filter(ee.Filter.And(dayToFilter, monthToFilter, yearToFilter))

    return x
