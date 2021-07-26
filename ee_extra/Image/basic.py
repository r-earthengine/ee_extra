"""Image module provide functions to manipulate ee.Image.
This module mimics the functionality provided by raster R
package (Robert J. Hijmans). The following functions are
implemented:

I. Creating ee.Image objects

- unstack: Create a list of ee.Image from a ee.ImageCollection.

II. Changing the resolution of ee.Image

- flip: Flip values horizontally or vertically
- rotate: Rotate values around the date-line (for lon/lat data)
- transpose: Transpose an ee.Image object

III. Cell based computation

- reclassify: Reclassify using a 'from-to-becomes' matrix.

IV. Spatial contextual computation

- distanceFromPoints: Shortest distance to any point in a set of points
- area: Compute area of cells (for longitude/latitude data)

V. Summarizing

- cellStats: Summarize an ee.Image cell values with a function.
- summary: Summary of the values of an ee.Image object (quartiles and mean).

VI. Accessing values of ee.Image object cells

- minValue: Get the minimum value of the cells of an ee.Image object.
- maxValue: Get the maximum value of the cells of an ee.Image object.
"""

from typing import Optional

import ee


def minvalue(x: ee.Image, scale: Optional[float] = None) -> float:
    """Get a minimum value.

    Returns the minimum value of an ee.Image. The return value
    will be an approximation if the polygon (x.geometry())
    contains too many pixels at the native scale.

    Args:
        x: An ee.Image
        scale: A nominal scale in meters of the projection
            to work in. Defaults image x$geometry()$projection()$nominalScale().
    Returns:
        An float number describing the x (ee.Image) minimum value.

    Examples:
        >>> import ee
        >>> import ee_extra
        >>> ee.Initialize()
        >>> img = ee.Image.random()
        >>> minvalue(img)
    """

    if scale is None:
        scale = x.geometry().projection().nominalScale()

    # Create a clean geometry i.e. geodesic = FALSE
    img_geom_local = x.geometry().getInfo()["coordinates"]
    ee_geom = ee.Geometry.Polygon(
        coords=img_geom_local,
        proj="EPSG:4326",
        evenOdd=True,
        maxError=1.0,
        geodesic=False,
    )

    # get min values
    minval = ee.Image.reduceRegion(
        image=x,
        reducer=ee.Reducer.min(),
        scale=scale,
        geometry=ee_geom,
        bestEffort=True,
    ).getInfo()

    return minval


def maxvalue(x: ee.Image, scale: Optional[float] = None) -> float:
    """
    Get a maximum value.

    Returns the maximum value of an ee.Image. The return value
    will be an approximation if the polygon (x.geometry())
    contains too many pixels at the native scale.

    Args:
        x: An ee.Image.
        scale: A nominal scale in meters of the projection to work in.
            Defaults image x$geometry()$projection()$nominalScale().

    Returns:
        An float number describing the x (ee.Image) maximum value.

    Examples:
        >>> import ee
        >>> import ee_extra
        >>> ee.Initialize()
        >>> img = ee.Image.random()
        >>> maxvalue(img)
    """

    if scale is None:
        scale = x.geometry().projection().nominalScale()

    # Create a clean geometry i.e. geodesic = FALSE
    img_geom_local = x.geometry().getInfo()["coordinates"]
    ee_geom = ee.Geometry.Polygon(
        coords=img_geom_local,
        proj="EPSG:4326",
        evenOdd=True,
        maxError=1.0,
        geodesic=False,
    )

    # get max values
    maxval = ee.Image.reduceRegion(
        image=x,
        reducer=ee.Reducer.max(),
        scale=scale,
        geometry=ee_geom,
        bestEffort=True,
    ).getInfo()

    return maxval
