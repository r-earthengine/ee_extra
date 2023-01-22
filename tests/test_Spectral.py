import unittest

import ee

from ee_extra.Spectral.core import *

ee.Initialize()

point = ee.Geometry.Point([-76.21, 3.45])
point2 = ee.Geometry.Point([143, -5])

# MYD Products are not in the GEE STAC anymore.
# They're commented for now.

datasets = {
    "COPERNICUS/S1_GRD": point,
    "JAXA/ALOS/PALSAR-2/Level2_2/ScanSAR": point2,
    "COPERNICUS/S2": point,
    "COPERNICUS/S2_HARMONIZED": point,
    "COPERNICUS/S2_SR": point,
    "COPERNICUS/S2_SR_HARMONIZED": point,
    "LANDSAT/LC08/C01/T1_SR": point,
    "LANDSAT/LC08/C01/T2_SR": point,
    "LANDSAT/LC08/C02/T1_L2": point,
    "LANDSAT/LC09/C02/T1_L2": point,
    "LANDSAT/LE07/C01/T1_SR": point,
    "LANDSAT/LE07/C01/T2_SR": point,
    "LANDSAT/LE07/C02/T1_L2": point,
    "LANDSAT/LT05/C01/T1_SR": point,
    "LANDSAT/LT05/C01/T2_SR": point,
    "LANDSAT/LT04/C01/T1_SR": point,
    "LANDSAT/LT04/C01/T2_SR": point,
    "MODIS/006/MOD09GQ": point,
    "MODIS/061/MOD09GQ": point,
    # "MODIS/006/MYD09GQ",
    "MODIS/006/MOD09GA": point,
    "MODIS/061/MOD09GA": point,
    # "MODIS/006/MYD09GA",
    "MODIS/006/MOD09Q1": point,
    "MODIS/061/MOD09Q1": point,
    # "MODIS/006/MYD09Q1",
    "MODIS/006/MOD09A1": point,
    "MODIS/061/MOD09A1": point,
    # "MODIS/006/MYD09A1",
    "MODIS/006/MCD43A4": point,
    # "MODIS/061/MCD43A4",
}

tasseledcap_datasets = [
    "COPERNICUS/S2",
    "MODIS/006/MCD43A4",
    "LANDSAT/LC09/C02/T1_L2",
    "LANDSAT/LC09/C02/T1_TOA",
    "LANDSAT/LC08/C02/T1_L2",
    "LANDSAT/LC08/C02/T2_L2",
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
        for dataset, geom in datasets.items():
            with self.subTest(i=dataset):
                x = ee.ImageCollection(dataset).filterBounds(geom)
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
                self.assertIsInstance(
                    tasseledCap(x), ee.imagecollection.ImageCollection
                )

                x = ee.ImageCollection(dataset).filterBounds(point).first()
                self.assertIsInstance(tasseledCap(x), ee.image.Image)

    def test_matchHistogram(self):
        """Test that histogram matching returns an image"""
        source = ee.Image("LANDSAT/LC08/C01/T1_TOA/LC08_047027_20160819")
        target = ee.Image("LANDSAT/LE07/C01/T1_TOA/LE07_046027_20150701")
        bands = {"B4": "B3", "B3": "B2", "B2": "B1"}
        matched = matchHistogram(source, target, bands=bands)
        self.assertIsInstance(matched, ee.image.Image)


if __name__ == "__main__":
    unittest.main()
