import ee
import unittest
from ee_extra.Spectral.core import *

ee.Initialize()

point = ee.Geometry.Point([-76.21, 3.45])

datasets = [
    "COPERNICUS/S2",
    "COPERNICUS/S2_SR",
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
    "MODIS/006/MYD09GQ",
    "MODIS/006/MOD09GA",
    "MODIS/006/MYD09GA",
    "MODIS/006/MOD09Q1",
    "MODIS/006/MYD09Q1",
    "MODIS/006/MOD09A1",
    "MODIS/006/MYD09A1",
    "MODIS/006/MCD43A4",
]


class Test(unittest.TestCase):
    """Tests for ee_extra package."""

    def test_spectralIndices(self):
        """Test the spectralIndices() method"""
        for dataset in datasets:
            with self.subTest(i=dataset):
                x = ee.ImageCollection(dataset).filterBounds(point)
                self.assertIsInstance(spectralIndices(x, "all"), ee.imagecollection.ImageCollection)
                self.assertIsInstance(spectralIndices(x.first(), "all"), ee.image.Image)

    def test_indices(self):
        """Test the indices() method"""
        self.assertIsInstance(indices(), dict)
        self.assertIsInstance(indices(True), dict)

    def test_listIndices(self):
        """Test the listIndices() method"""
        self.assertIsInstance(listIndices(), list)
        self.assertIsInstance(listIndices(True), list)


if __name__ == "__main__":
    unittest.main()
