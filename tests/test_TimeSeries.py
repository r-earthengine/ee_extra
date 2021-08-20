import unittest

import ee

from ee_extra.TimeSeries.core import *

ee.Initialize()

f1 = ee.Feature(ee.Geometry.Point([3.984770, 48.767221]).buffer(50), {"ID": "A"})
f2 = ee.Feature(ee.Geometry.Point([4.101367, 48.748076]).buffer(50), {"ID": "B"})
fc = ee.FeatureCollection([f1, f2])

reducers = [
    ee.Reducer.mean(),
    ee.Reducer.max(),
    ee.Reducer.min(),
    ee.Reducer.median(),
    ee.Reducer.first(),
]

ic = (
    ee.ImageCollection("COPERNICUS/S2_SR")
    .filterBounds(fc)
    .filterDate("2020-01-01", "2020-02-01")
)


class Test(unittest.TestCase):
    """Tests for ee_extra package."""

    def test_getTimeSeriesByRegion(self):
        """Test the getTimeSeriesByRegion() method"""
        ts = getTimeSeriesByRegion(
            x=ic, reducer=reducers, geometry=fc, bands=["B4", "B8"], scale=10
        )
        self.assertIsInstance(ts, ee.featurecollection.FeatureCollection)

    def test_getTimeSeriesByRegions(self):
        """Test the getTimeSeriesByRegions() method"""
        ts = getTimeSeriesByRegions(
            x=ic, reducer=reducers, collection=fc, bands=["B4", "B8"], scale=10
        )
        self.assertIsInstance(ts, ee.featurecollection.FeatureCollection)


if __name__ == "__main__":
    unittest.main()
