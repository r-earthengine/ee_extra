import ee
import unittest

from ee_extra.QA.metrics import *

ee.Initialize()


class Test(unittest.TestCase):
    """Tests for QA module."""

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
            if metric is ERGAS:
                value = metric(img, modified, h=30, l=30)
            else:
                value = metric(img, modified)
            self.assertIsInstance(value, (ee.Number, ee.Dictionary))
