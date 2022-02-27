import unittest

import ee

from ee_extra.Algorithms.core import panSharpen

ee.Initialize()


class Test(unittest.TestCase):
    """Tests for Algorithms module."""

    def test_pansharpen_with_image(self):
        """Pansharpening an image should return an image."""
        img = ee.Image("LANDSAT/LC08/C01/T1_TOA/LC08_047027_20160819")
        sharp = panSharpen(img)
        self.assertIsInstance(sharp, ee.Image)

    def test_pansharpen_with_collection(self):
        """Pansharpening an collection should return an collection"""
        col = ee.ImageCollection("LANDSAT/LC08/C01/T1_TOA").limit(10)
        sharp = panSharpen(col)
        self.assertIsInstance(sharp, ee.ImageCollection)

    def test_pansharpen_with_unsupported_platform(self):
        """Pansharpening an unsupported platform should raise an AttributeError."""
        unsupp = ee.ImageCollection("COPERNICUS/S2_SR").limit(10)
        
        with self.assertRaises(AttributeError):
            panSharpen(unsupp)

    def test_pansharpen_with_qa(self):
        """Pansharpening an image or collection with QA metrics should return the input type."""
        img = ee.Image("LANDSAT/LC08/C01/T1_TOA/LC08_047027_20160819")
        sharp = panSharpen(img, qa=["RMSE", "UIQI", "ERGAS"])
        self.assertIsInstance(sharp, ee.Image)

        col = ee.ImageCollection("LANDSAT/LC08/C01/T1_TOA").limit(10)
        sharp = panSharpen(col, qa=["RMSE", "UIQI", "ERGAS"])
        self.assertIsInstance(sharp, ee.ImageCollection)

    def test_pansharpen_with_bad_qa(self):
        """Pansharpening with invalid QA names should raise an AttributeError"""
        img = ee.Image("LANDSAT/LC08/C01/T1_TOA/LC08_047027_20160819")
        
        with self.assertRaises(AttributeError):
            panSharpen(img, qa=["not_a_real_metric"])


if __name__ == "__main__":
    unittest.main()