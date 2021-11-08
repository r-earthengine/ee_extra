import unittest

from ee_extra import translate


class Test(unittest.TestCase):
    """Tests translate package"""

    def test_plus_sign01(self):
        """Test translation of plus sign"""
        text = """
        // Load a Landsat 8 image and select the panchromatic band.
        var image = ee.Image('LANDSAT/LC08/C01/T1/LC08_044034_20140318').select('B8');

        // Compute the image gradient in the X and Y directions.
        var xyGrad = image.gradient();

        // Compute the magnitude of the gradient.
        var gradient = xyGrad.select('x').pow(2)
                .add(xyGrad.select('y').pow(2)).sqrt();

        // Compute the direction of the gradient.
        var direction = xyGrad.select('y').atan2(xyGrad.select('x'));

        // Display the results.
        Map.setCenter(-122.054, 37.7295, 10);
        Map.addLayer(direction, {min: -2, max: 2, format: 'png'}, 'direction');
        Map.addLayer(gradient, {min: -7, max: 7, format: 'png'}, 'gradient');
        """
        text = text.replace("\n    ", "")
        self.assertIsInstance(translate(text, black=False), str)

if __name__ == "__main__":
    unittest.main()