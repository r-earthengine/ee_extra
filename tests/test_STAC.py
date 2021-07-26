import ee
import unittest
from ee_extra.STAC.core import *

ee.Initialize()

point = ee.Geometry.Point([-76.21, 3.45])

datasets = listDatasets()

class Test(unittest.TestCase):
    """Tests for ee_extra package."""

    def test_listDatasets(self):
        """Test the listDatasets() method"""
        self.assertIsInstance(listDatasets(), list)

    def test_getCitation(self):
        """Test the getCitation() method"""
        for dataset in datasets:
            with self.subTest(i=dataset):
                x = ee.ImageCollection(dataset).filterBounds(point)
                self.assertIsInstance(getCitation(x), str)
                self.assertIsInstance(getCitation(x.first()), str)

    def test_getDOI(self):
        """Test the getDOI() method"""
        for dataset in datasets:
            with self.subTest(i=dataset):
                x = ee.ImageCollection(dataset).filterBounds(point)
                self.assertIsInstance(getDOI(x), str)
                self.assertIsInstance(getDOI(x.first()), str)

    def test_getOffsetParams(self):
        """Test the getOffsetParams() method"""
        for dataset in datasets:
            with self.subTest(i=dataset):
                x = ee.ImageCollection(dataset).filterBounds(point)
                self.assertIsInstance(getOffsetParams(x), dict)
                self.assertIsInstance(getOffsetParams(x.first()), dict)

    def test_getScaleParams(self):
        """Test the getScaleParams() method"""
        for dataset in datasets:
            with self.subTest(i=dataset):
                x = ee.ImageCollection(dataset).filterBounds(point)
                self.assertIsInstance(getScaleParams(x), dict)
                self.assertIsInstance(getScaleParams(x.first()), dict)

    def test_getSTAC(self):
        """Test the getSTAC() method"""
        for dataset in datasets:
            with self.subTest(i=dataset):
                x = ee.ImageCollection(dataset).filterBounds(point)
                self.assertIsInstance(getSTAC(x), dict)
                self.assertIsInstance(getSTAC(x.first()), dict)

    def test_scaleAndOffset(self):
        """Test the scaleAndOffset() method"""
        for dataset in datasets:
            with self.subTest(i=dataset):
                x = ee.ImageCollection(dataset).filterBounds(point)
                self.assertIsInstance(scaleAndOffset(x), ee.imagecollection.ImageCollection)
                self.assertIsInstance(scaleAndOffset(x.first()), ee.image.Image)


if __name__ == "__main__":
    unittest.main()
