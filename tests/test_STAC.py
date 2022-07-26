import unittest

import ee

from ee_extra.STAC.core import *

ee.Initialize()

point = ee.Geometry.Point([-76.21, 3.45])

# MYD Products are not in the GEE STAC anymore.
# They're commented for now.

datasets = [
    "COPERNICUS/S2",
    "COPERNICUS/S2_SR",
    "COPERNICUS/S2_SR_HARMONIZED",
    "LANDSAT/LC08/C01/T1_SR",
    "LANDSAT/LC08/C01/T2_SR",
    "LANDSAT/LC08/C02/T1_L2",
    "LANDSAT/LE07/C01/T1_SR",
    "LANDSAT/LE07/C01/T2_SR",
    "LANDSAT/LE07/C02/T1_L2",
    "LANDSAT/LT05/C01/T1_SR",
    "LANDSAT/LT05/C01/T2_SR",
    "LANDSAT/LT04/C01/T1_SR",
    "LANDSAT/LT04/C01/T2_SR",
    "MODIS/006/MOD09GQ",
    # "MODIS/006/MYD09GQ",
    "MODIS/006/MOD09GA",
    # "MODIS/006/MYD09GA",
    "MODIS/006/MOD09Q1",
    # "MODIS/006/MYD09Q1",
    "MODIS/006/MOD09A1",
    # "MODIS/006/MYD09A1",
    "MODIS/006/MCD43A4",
]


class Test(unittest.TestCase):
    """Tests for ee_extra package."""

    def test_listDatasets(self):
        """Test the listDatasets() method"""
        self.assertIsInstance(listDatasets(), list)

    def test_getCitation(self):
        """Test the getCitation() method"""
        for dataset in datasets:
            with self.subTest(dataset=dataset):
                x = ee.ImageCollection(dataset).filterBounds(point)
                self.assertIsInstance(getCitation(x), str)
                self.assertIsInstance(getCitation(x.first()), str)

    def test_getDOI(self):
        """Test the getDOI() method"""
        for dataset in datasets:
            with self.subTest(dataset=dataset):
                x = ee.ImageCollection(dataset).filterBounds(point)
                self.assertIsInstance(getDOI(x), str)
                self.assertIsInstance(getDOI(x.first()), str)

    def test_getOffsetParams(self):
        """Test the getOffsetParams() method"""
        for dataset in datasets:
            with self.subTest(dataset=dataset):
                x = ee.ImageCollection(dataset).filterBounds(point)
                self.assertIsInstance(getOffsetParams(x), dict)
                self.assertIsInstance(getOffsetParams(x.first()), dict)

    def test_getScaleParams(self):
        """Test the getScaleParams() method"""
        for dataset in datasets:
            with self.subTest(dataset=dataset):
                x = ee.ImageCollection(dataset).filterBounds(point)
                self.assertIsInstance(getScaleParams(x), dict)
                self.assertIsInstance(getScaleParams(x.first()), dict)

    def test_getSTAC(self):
        """Test the getSTAC() method"""
        for dataset in datasets:
            with self.subTest(dataset=dataset):
                x = ee.ImageCollection(dataset).filterBounds(point)
                self.assertIsInstance(getSTAC(x), dict)
                self.assertIsInstance(getSTAC(x.first()), dict)

    def test_scaleAndOffset(self):
        """Test the scaleAndOffset() method"""
        for dataset in datasets:
            with self.subTest(dataset=dataset):
                x = ee.ImageCollection(dataset).filterBounds(point)
                self.assertIsInstance(
                    scaleAndOffset(x), ee.imagecollection.ImageCollection
                )
                self.assertIsInstance(scaleAndOffset(x.first()), ee.image.Image)


if __name__ == "__main__":
    unittest.main()
