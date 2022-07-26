import ee
import unittest

from ee_extra.QA.metrics import *
from ee_extra.QA.clouds import *

ee.Initialize()

point = ee.Geometry.Point([-76.21, 3.45])

datasets = [
    # "COPERNICUS/S2",
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
    # "MODIS/006/MOD09GQ",
    # "MODIS/006/MYD09GQ",
    "MODIS/006/MOD09GA",
    # "MODIS/006/MYD09GA",
    "MODIS/006/MOD09Q1",
    # "MODIS/006/MYD09Q1",
    "MODIS/006/MOD09A1",
    # "MODIS/006/MYD09A1",
    # "MODIS/006/MCD43A4",
]

class Test(unittest.TestCase):
    """Tests for QA module."""

    def test_cloud_masking(self):
        """Test the getCitation() method"""
        for dataset in datasets:
            with self.subTest(dataset=dataset):
                x = ee.ImageCollection(dataset).filterBounds(point)
                self.assertIsInstance(maskClouds(x), ee.imagecollection.ImageCollection)
                self.assertIsInstance(maskClouds(x.first()), ee.image.Image)

    def test_list_metrics(self):
        """Test that listMetrics returns a valid dictionary"""
        metrics = listMetrics()

        self.assertIn("MSE", metrics.keys())
        self.assertEqual(MSE, metrics["MSE"])

    def test_get_metrics(self):
        """Test that getMetrics returns matches"""
        mse = getMetrics(["MSE"])[0]
        self.assertIs(mse, MSE)

    def test_all_metrics(self):
        """Test that all metrics run"""
        metrics = listMetrics().values()

        img = ee.Image("LANDSAT/LC08/C01/T1_TOA/LC08_047027_20160819")
        modified = ee.Image("LANDSAT/LC08/C01/T1_TOA/LC08_047027_20160819")

        for metric in metrics:
            value = metric(img, modified)
            self.assertIsInstance(value, (ee.Number, ee.Dictionary))
