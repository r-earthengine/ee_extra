import ee
import unittest
from ee_extra.ImageCollection.core import *

ee.Initialize()

point = ee.Geometry.Point([-76.21, 3.45])
x = ee.ImageCollection("COPERNICUS/S2_SR").filterBounds(point)


class Test(unittest.TestCase):
    """Tests for ee_extra package."""

    def test_closest(self):
        """Test the closest() method"""
        test = closest(x, "2020-01-01")
        self.assertIsInstance(test, ee.imagecollection.ImageCollection)


if __name__ == "__main__":
    unittest.main()
