import unittest

import ee

from ee_extra.Spectral.core import *

ee.Initialize()

point = ee.Geometry.Point([-76.21, 3.45])

# MYD Products are not in the GEE STAC anymore.
# They're commented for now.

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
    #"MODIS/006/MYD09GQ",
    "MODIS/006/MOD09GA",
    #"MODIS/006/MYD09GA",
    "MODIS/006/MOD09Q1",
    #"MODIS/006/MYD09Q1",
    "MODIS/006/MOD09A1",
    #"MODIS/006/MYD09A1",
    "MODIS/006/MCD43A4",
]

tasseledcap_datasets = [
    "COPERNICUS/S2",
    "MODIS/006/MCD43A4",
    "LANDSAT/LC08/C01/T1_TOA",
    "LANDSAT/LC08/C01/T1_RT_TOA",
    "LANDSAT/LC08/C01/T2_TOA",
    "LANDSAT/LE07/C01/T1_TOA",
    "LANDSAT/LE07/C01/T1_RT_TOA",
    "LANDSAT/LE07/C01/T2_TOA",
    "LANDSAT/LT05/C01/T1",
    "LANDSAT/LT05/C01/T2",
    "LANDSAT/LT04/C02/T1_L2",
    "LANDSAT/LT04/C02/T2_L2",
    "LANDSAT/LT04/C01/T1",
    "LANDSAT/LT04/C01/T2",
]


class Test(unittest.TestCase):
    """Tests for ee_extra package."""

    def test_spectralIndices(self):
        """Test the spectralIndices() method"""
        for dataset in datasets:
            with self.subTest(i=dataset):
                x = ee.ImageCollection(dataset).filterBounds(point)
                self.assertIsInstance(
                    spectralIndices(x, "all"), ee.imagecollection.ImageCollection
                )
                self.assertIsInstance(spectralIndices(x.first(), "all"), ee.image.Image)

    def test_indices(self):
        """Test the indices() method"""
        self.assertIsInstance(indices(), dict)
        self.assertIsInstance(indices(True), dict)

    def test_listIndices(self):
        """Test the listIndices() method"""
        self.assertIsInstance(listIndices(), list)
        self.assertIsInstance(listIndices(True), list)

    def test_tasseledCap(self):
        """Test the tasseledCap() method"""
        for dataset in tasseledcap_datasets:
            with self.subTest(i=dataset):
                x = ee.ImageCollection(dataset).filterBounds(point).limit(10)
                self.assertIsInstance(tasseledCap(x), ee.imagecollection.ImageCollection)

                x = ee.ImageCollection(dataset).filterBounds(point).first()
                self.assertIsInstance(tasseledCap(x), ee.image.Image)


if __name__ == "__main__":
    unittest.main()
