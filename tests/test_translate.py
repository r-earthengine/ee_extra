from ee_extra import translate
from pprint import pprint
import unittest
import ee

ee.Initialize()

class Test(unittest.TestCase):
    """Tests translate package"""
    def test_plus_sign01(self):
        """Test translation of plus sign"""
        text = """
        var uri = 'gs://gcp-public-data-landsat/LC08/01/001/002/' +
            'LC08_L1GT_001002_20160817_20170322_01_T2/' +
            'LC08_L1GT_001002_20160817_20170322_01_T2_B5.TIF';
        var cloudImage = ee.Image.loadGeoTIFF(uri);
        print(cloudImage);
        """
        self.assertIsInstance(translate(text), str)
        
    def test_plus_sign02(self):
        """Test translation of plus sign"""

        text = """
        var cover = ee.Image('MODIS/051/MCD12Q1/2012_01_01').select('Land_Cover_Type_1');
        // Define an SLD style of discrete intervals to apply to the image.
        var sld_intervals =
        '<RasterSymbolizer>' +
        '<ColorMap type="intervals" extended="false">' +
            '<ColorMapEntry color="#aec3d4" quantity="0" label="Water"/>' +
            '<ColorMapEntry color="#152106" quantity="1" label="Evergreen Needleleaf Forest"/>' +
            '<ColorMapEntry color="#225129" quantity="2" label="Evergreen Broadleaf Forest"/>' +
            '<ColorMapEntry color="#369b47" quantity="3" label="Deciduous Needleleaf Forest"/>' +
            '<ColorMapEntry color="#30eb5b" quantity="4" label="Deciduous Broadleaf Forest"/>' +
            '<ColorMapEntry color="#387242" quantity="5" label="Mixed Deciduous Forest"/>' +
            '<ColorMapEntry color="#6a2325" quantity="6" label="Closed Shrubland"/>' +
            '<ColorMapEntry color="#c3aa69" quantity="7" label="Open Shrubland"/>' +
            '<ColorMapEntry color="#b76031" quantity="8" label="Woody Savanna"/>' +
            '<ColorMapEntry color="#d9903d" quantity="9" label="Savanna"/>' +
            '<ColorMapEntry color="#91af40" quantity="10" label="Grassland"/>' +
            '<ColorMapEntry color="#111149" quantity="11" label="Permanent Wetland"/>' +
            '<ColorMapEntry color="#cdb33b" quantity="12" label="Cropland"/>' +
            '<ColorMapEntry color="#cc0013" quantity="13" label="Urban"/>' +
            '<ColorMapEntry color="#33280d" quantity="14" label="Crop, Natural Veg. Mosaic"/>' +
            '<ColorMapEntry color="#d7cdcc" quantity="15" label="Permanent Snow, Ice"/>' +
            '<ColorMapEntry color="#f7e084" quantity="16" label="Barren, Desert"/>' +
            '<ColorMapEntry color="#6f6f6f" quantity="17" label="Tundra"/>' +
        '</ColorMap>' +
        '</RasterSymbolizer>';
        """
        self.assertIsInstance(translate(text), str)

    def test_dot_conversion01(self):
        """Test translation of plus dot sign"""
        text = """
        // Fetch a digital elevation model.
        var image = ee.Image('CGIAR/SRTM90_V4');

        // Specify region by a linear ring and set display CRS as Web Mercator.
        var thumbnail3 = image.getThumbURL({
        'min': 0,
        'max': 3000,
        'palette': ['00A600','63C600','E6E600','E9BD3A','ECB176','EFC2B3','F2F2F2'],
        'region': ee.Geometry.LinearRing([[-84.6, 15.7], [-84.6, -55.9], [-32.9, -55.9]]),
        'dimensions': 500,
        'crs': 'EPSG:3857'
        });
        print('Linear ring region and specified crs', thumbnail3);
        """
        self.assertIsInstance(translate(text), str)

    def test_line_breaks01(self):
        text = """
        // Load a Landsat 8 image, select the NIR band, threshold, display.
        var image = ee.Image('LANDSAT/LC08/C01/T1_TOA/LC08_044034_20140318')
                    .select(4).gt(0.2);

        // Define a kernel.
        var kernel = ee.Kernel.circle({radius: 1});

        // Perform an erosion followed by a dilation, display.
        var opened = image
                    .focal_min({kernel: kernel, iterations: 2})
                    .focal_max({kernel: kernel, iterations: 2});
        """
        self.assertIsInstance(translate(text), str)
    
    def test_external_libs_01(self):
        text = """
        // Create a list of weights for a 9x9 kernel.
        var row = [1, 1, 1, 1, 1, 1, 1, 1, 1];
        // The center of the kernel is zero.
        var centerRow = [1, 1, 1, 1, 0, 1, 1, 1, 1];
        // Assemble a list of lists: the 9x9 kernel weights as a 2-D matrix.
        var rows = [row, row, row, row, centerRow, row, row, row, row];
        // Create the kernel from the weights.
        // Non-zero weights represent the spatial neighborhood.
        var kernel = ee.Kernel.fixed(9, 9, rows, -4, -4, false);

        // Convert the neighborhood into multiple bands.
        var neighs = nir.neighborhoodToBands(kernel);

        // Compute local Geary's C, a measure of spatial association.
        var gearys = nir.subtract(neighs).pow(2).reduce(ee.Reducer.sum())
                    .divide(Math.pow(9, 2));
        """
        self.assertIsInstance(translate(text), str)

    def test_dot_conversion02(self):
        text = """
        // A rectangle representing Bangui, Central African Republic.
        var geometry = ee.Geometry.Rectangle([18.5229, 4.3491, 18.5833, 4.4066]);

        // Create a source image where the geometry is 1, everything else is 0.
        var sources = ee.Image().toByte().paint(geometry, 1);

        // Mask the sources image with itself.
        sources = sources.selfMask();

        // The cost data is generated from classes in ESA/GLOBCOVER.
        var cover = ee.Image('ESA/GLOBCOVER_L4_200901_200912_V2_3').select(0);

        // Classes 60, 80, 110, 140 have cost 1.
        // Classes 40, 90, 120, 130, 170 have cost 2.
        // Classes 50, 70, 150, 160 have cost 3.
        var beforeRemap = [60, 80, 110, 140,
                        40, 90, 120, 130, 170,
                        50, 70, 150, 160];
        var afterRemap = [1, 1, 1, 1,
                        2, 2, 2, 2, 2,
                        3, 3, 3, 3];
        var cost = cover.remap(beforeRemap, afterRemap, 0);

        // Compute the cumulative cost to traverse the land cover.
        var cumulativeCost = cost.cumulativeCost({
        source: sources,
        maxDistance: 80 * 1000  // 80 kilometers
        });
        """
        self.assertIsInstance(translate(text), str)

if __name__ == "__main__":
    unittest.main()
