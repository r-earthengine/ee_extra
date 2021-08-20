from typing import Any, List, Optional, Union

import ee


def getTimeSeriesByRegion(
    x: ee.ImageCollection,
    reducer: Any,
    bands: Optional[Union[str, List[str]]] = None,
    geometry: Optional[Union[ee.Geometry, ee.Feature, ee.FeatureCollection]] = None,
    scale: Optional[Union[int, float]] = None,
    crs: Optional[Any] = None,
    crsTransform: Optional[Any] = None,
    bestEffort: bool = False,
    maxPixels: Union[int, float] = 1e12,
    tileScale: int = 1,
    dateColumn: str = "date",
    dateFormat: str = "ISO",
    naValue: Union[int, float] = -9999,
):
    """Gets the time series by region for the given image collection and geometry (feature
    or feature collection are also supported) according to the specified reducer (or
    reducers).

    Args:
        x : Image collection to get the time series from.
        reducer : Reducer or list of reducers to use for region reduction.
        bands : Selection of bands to get the time series from. Defaults to all bands in
            the image collection.
        geometry : Geometry to perform the region reduction. If ee.Feature or
            ee.FeatureCollection, the geometry() method is called. In order to get
            reductions by each feature please see the getTimeSeriesByRegions() method.
            Defaults to the footprint of the first band for each image in the collection.
        scale : Nomical scale in meters.
        crs : The projection to work in. If unspecified, the projection of the image's
            first band is used. If specified in addition to scale, rescaled to the
            specified scale.
        crsTransform : The list of CRS transform values. This is a row-major ordering of
            the 3x2 transform matrix. This option is mutually exclusive with 'scale', and
            replaces any transform already set on the projection.
        bestEffort : If the polygon would contain too many pixels at the given scale,
            compute and use a larger scale which would allow the operation to succeed.
        maxPixels : The maximum number of pixels to reduce.
        tileScale : A scaling factor used to reduce aggregation tile size; using a larger
            tileScale (e.g. 2 or 4) may enable computations that run out of memory with
            the default.
        dateColumn : Output name of the date column.
        dateFormat : Output format of the date column. Defaults to ISO. Available options:
            'ms' (for milliseconds), 'ISO' (for ISO Standard Format) or a custom format
            pattern.
        naValue : Value to use as NA when the region reduction doesn't retrieve a value
            due to masked pixels.

    Returns:
        Time series by region retrieved as a Feature Collection.

    Examples:
        >>> import ee
        >>> from ee_extra.TimeSeries.core import getTimeSeriesByRegion
        >>> ee.Initialize()
        >>> f1 = ee.Feature(ee.Geometry.Point([3.984770,48.767221]).buffer(50),{'ID':'A'})
        >>> f2 = ee.Feature(ee.Geometry.Point([4.101367,48.748076]).buffer(50),{'ID':'B'})
        >>> fc = ee.FeatureCollection([f1,f2])
        >>> S2 = (ee.ImageCollection('COPERNICUS/S2_SR')
        ...      .filterBounds(fc)
        ...      .filterDate('2020-01-01','2021-01-01'))
        >>> ts = getTimeSeriesByRegion(S2,
        ...     reducer = [ee.Reducer.mean(),ee.Reducer.median()],
        ...     geometry = fc,
        ...     bands = ['B4','B8'],
        ...     scale = 10)
    """
    if bands != None:
        if not isinstance(bands, list):
            bands = [bands]
        x = x.select(bands)

    if not isinstance(reducer, list):
        reducer = [reducer]

    if not isinstance(geometry, ee.geometry.Geometry):
        geometry = geometry.geometry()

    collections = []

    for red in reducer:

        reducerName = red.getOutputs().get(0)

        def reduceImageCollectionByRegion(img):
            dictionary = img.reduceRegion(
                red,
                geometry,
                scale,
                crs,
                crsTransform,
                bestEffort,
                maxPixels,
                tileScale,
            )
            if dateFormat == "ms":
                date = ee.Date(img.get("system:time_start")).millis()
            elif dateFormat == "ISO":
                date = ee.Date(img.get("system:time_start")).format()
            else:
                date = ee.Date(img.get("system:time_start")).format(dateFormat)
            return ee.Feature(None, dictionary).set(
                {dateColumn: date, "reducer": reducerName}
            )

        collections.append(ee.FeatureCollection(x.map(reduceImageCollectionByRegion)))

    flattenfc = ee.FeatureCollection(collections).flatten()

    def setNA(feature):
        feature = ee.Algorithms.If(
            condition=feature.propertyNames().size().eq(3),
            trueCase=feature.set(
                ee.Dictionary.fromLists(bands, [naValue] * len(bands))
            ),
            falseCase=feature,
        )
        feature = ee.Feature(feature)
        return feature

    return flattenfc.map(setNA)


def getTimeSeriesByRegions(
    x: ee.ImageCollection,
    reducer: Any,
    collection: ee.FeatureCollection,
    bands: Optional[Union[str, List[str]]] = None,
    scale: Optional[Union[int, float]] = None,
    crs: Optional[Any] = None,
    crsTransform: Optional[Any] = None,
    tileScale: int = 1,
    dateColumn: str = "date",
    dateFormat: str = "ISO",
    naValue: Union[int, float] = -9999,
):
    """Gets the time series by regions for the given image collection and feature
    collection according to the specified reducer (or reducers).

    Args:
        x : Image collection to get the time series from.
        reducer : Reducer or list of reducers to use for region reduction.
        collection : Feature Collection to perform the reductions on. Image reductions are
            applied to each feature in the collection.
        bands : Selection of bands to get the time series from. Defaults to all bands in
            the image collection.
        scale : Nomical scale in meters.
        crs : The projection to work in. If unspecified, the projection of the image's
            first band is used. If specified in addition to scale, rescaled to the
            specified scale.
        crsTransform : The list of CRS transform values. This is a row-major ordering of
            the 3x2 transform matrix. This option is mutually exclusive with 'scale', and
            replaces any transform already set on the projection.
        tileScale : A scaling factor used to reduce aggregation tile size; using a larger
            tileScale (e.g. 2 or 4) may enable computations that run out of memory with
            the default.
        dateColumn : Output name of the date column.
        dateFormat : Output format of the date column. Defaults to ISO. Available options:
            'ms' (for milliseconds), 'ISO' (for ISO Standard Format) or a custom format
            pattern.
        naValue : Value to use as NA when the region reduction doesn't retrieve a value
            due to masked pixels.

    Returns:
        Time series by regions retrieved as a Feature Collection.

    Examples:
        >>> import ee
        >>> from ee_extra.TimeSeries.core import getTimeSeriesByRegions
        >>> ee.Initialize()
        >>> f1 = ee.Feature(ee.Geometry.Point([3.984770,48.767221]).buffer(50),{'ID':'A'})
        >>> f2 = ee.Feature(ee.Geometry.Point([4.101367,48.748076]).buffer(50),{'ID':'B'})
        >>> fc = ee.FeatureCollection([f1,f2])
        >>> S2 = (ee.ImageCollection('COPERNICUS/S2_SR')
        ...      .filterBounds(fc)
        ...      .filterDate('2020-01-01','2021-01-01'))
        >>> ts = getTimeSeriesByRegions(S2,
        ...     reducer = [ee.Reducer.mean(),ee.Reducer.median()],
        ...     collection = fc,
        ...     bands = ['B3','B8'],
        ...     scale = 10)
    """
    if bands != None:
        if not isinstance(bands, list):
            bands = [bands]
        x = x.select(bands)

    if not isinstance(reducer, list):
        reducer = [reducer]

    if not isinstance(collection, ee.featurecollection.FeatureCollection):
        raise Exception("Parameter collection must be an ee.FeatureCollection!")

    props = collection.first().propertyNames()

    collections = []

    imgList = x.toList(x.size())

    for red in reducer:

        reducerName = red.getOutputs().get(0)

        def reduceImageCollectionByRegions(img):

            img = ee.Image(img)

            if len(bands) == 1:
                img = img.addBands(ee.Image(naValue).rename("eemontTemporal"))

            fc = img.reduceRegions(collection, red, scale, crs, crsTransform, tileScale)

            if dateFormat == "ms":
                date = ee.Date(img.get("system:time_start")).millis()
            elif dateFormat == "ISO":
                date = ee.Date(img.get("system:time_start")).format()
            else:
                date = ee.Date(img.get("system:time_start")).format(dateFormat)

            def setProperties(feature):
                return feature.set({dateColumn: date, "reducer": reducerName})

            return fc.map(setProperties)

        collections.append(x.map(reduceImageCollectionByRegions).flatten())

    flattenfc = ee.FeatureCollection(collections).flatten()

    def setNA(feature):
        feature = ee.Algorithms.If(
            condition=feature.propertyNames().size().eq(props.size().add(2)),
            trueCase=feature.set(
                ee.Dictionary.fromLists(bands, [naValue] * len(bands))
            ),
            falseCase=feature,
        )
        feature = ee.Feature(feature)
        return feature

    flattenfc = flattenfc.map(setNA)
    flattenfc = flattenfc.select(props.cat(["reducer", dateColumn]).cat(bands))

    return flattenfc
