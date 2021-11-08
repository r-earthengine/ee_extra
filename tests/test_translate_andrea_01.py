import unittest

from ee_extra import translate


class Test(unittest.TestCase):
    """Tests translate package"""

    def test_plus_sign01(self):
        """Test translation of plus sign"""
        text = """
        // Create arbitrary constant images.
        var constant1 = ee.Image(1);
        var constant2 = ee.Image(2);

        // Create a collection by giving a list to the constructor.
        var collectionFromConstructor = ee.ImageCollection([constant1, constant2]);
        print('collectionFromConstructor: ', collectionFromConstructor);

        // Create a collection with fromImages().
        var collectionFromImages = ee.ImageCollection.fromImages(
        [ee.Image(3), ee.Image(4)]);
        print('collectionFromImages: ', collectionFromImages);

        // Merge two collections.
        var mergedCollection = collectionFromConstructor.merge(collectionFromImages);
        print('mergedCollection: ', mergedCollection);

        // Create a toy FeatureCollection
        var features = ee.FeatureCollection(
        [ee.Feature(null, {foo: 1}), ee.Feature(null, {foo: 2})]);

        // Create an ImageCollection from the FeatureCollection
        // by mapping a function over the FeatureCollection.
        var images = features.map(function(feature) {
        return ee.Image(ee.Number(feature.get('foo')));
        });

        // Print the resultant collection.
        print('Image collection: ', images);    
        """
        text = text.replace("\n    ", "")
        self.assertIsInstance(translate(text, black=False), str)


if __name__ == "__main__":
    unittest.main()
