# from ee_extra.JavaScript.merge import require
# from ee_extra.JavaScript.install import install
import unittest

from ee_extra import translate


class Test(unittest.TestCase):
    """Tests translate package"""

    def test_plus_sign01(self):
        """Test translation of plus sign"""
        text = """
        var dasdas = 2
        var uri = 'gs://gcp-public-data-landsat/LC08/01/001/002/' +  
            'LC08_L1GT_001002_20160817_20170322_01_T2/' +  
            'LC08_L1GT_001002_20160817_20170322_01_T2_B5.TIF';  
        var cloudImage = ee.Image.loadGeoTIFF(uri);
        print(cloudImage);
        var uri2 = 'gs://gcp-public-data-landsat/LC08/01/001/002/' +  
            'LC08_L1GT_001002_20160817_20170322_01_T2/'    
            
        var uri2 = 'gs://gcp-public-data-landsat/LC08/01/001/002/' +  
            'LC08_L1GT_001002_20160817_20170322_01_T2/'    
        """
        text = text.replace("\n    ", "")
        self.assertIsInstance(translate(text, black=False), str)

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
        text = text.replace("\n    ", "")
        self.assertIsInstance(translate(text, black=False), str)

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
        text = text.replace("\n    ", "")
        self.assertIsInstance(translate(text, black=False), str)

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
        self.assertIsInstance(translate(text, black=False), str)

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
        self.assertIsInstance(translate(text, black=False), str)

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
        self.assertIsInstance(translate(text, black=False), str)

    def test_iterators(self):
        """Test iterators"""
        text = """
        // normal loops
        var numbers = [45, 4, 9, 16, 25];

        // case01
        for (var i = 0; i < 5; i++) {
        numbers[i]
        }

        // case02
        for (var i = 0; i < 5; i++) { numbers[i]
        }

        // case03
        for (var i = 0; i < 5; i++)
        {
        numbers[i]
        }

        // case04
        for (var i = 0; i < 5; i++) 
            numbers[i]

        // case05
        for (var i = 0; i < 5; i++) numbers[i]    

        // case06
        for (var i = 0; var lesly = 10; i < 5; i++) 
            numbers[i]

        // case07
        var i = 0;
        var len = numbers.length;
        var text = "";
        for (; i < len; ) {
        text += numbers[i] + "<br>";
        // print(text)
        i++;
        }

        // case08
        for (var i = 0, len = numbers.length, text = ""; i < len; i++) {
        text += numbers[i] + "<br>";
        }

        ////////////
        // in loops
        ////////////
        var person = {fname:"John", lname:"Doe", age:25};
        var text = "";
        for (var x in person) {
        text += person[x];
        }

        ////////////
        // while loops
        ////////////
        var i = 0;
        var text = "";
        while (i < 10) {
        text += "The number is " + i;
        print(text)
        i++;
        }
        """
        self.assertIsInstance(translate(text, black=False), str)

    def test_ltrend_01(self):
        """LandTrendr function"""
        text = """
        var harmonizationRoy = function(oli) {
        var slopes = ee.Image.constant([0.9785, 0.9542, 0.9825, 1.0073, 1.0171, 0.9949]);        // RMA - create an image of slopes per band for L8 TO L7 regression line - David Roy
        var itcp = ee.Image.constant([-0.0095, -0.0016, -0.0022, -0.0021, -0.0030, 0.0029]);     // RMA - create an image of y-intercepts per band for L8 TO L7 regression line - David Roy
        //var slopes = ee.Image.constant([0.885, 0.9317, 0.9372, 0.8339, 0.8639, 0.9165]);       // least squares OLI to ETM+
        //var itcp = ee.Image.constant([0.0183, 0.0123, 0.0123, 0.0448, 0.0306, 0.0116]);        // least squares OLI to ETM+
        var y = oli.select(['B2','B3','B4','B5','B6','B7'],['B1', 'B2', 'B3', 'B4', 'B5', 'B7']) // select OLI bands 2-7 and rename them to match L7 band names
                    .resample('bicubic')                                                          // ...resample the L8 bands using bicubic
                    .subtract(itcp.multiply(10000)).divide(slopes)                                // ...multiply the y-intercept bands by 10000 to match the scale of the L7 bands then apply the line equation - subtract the intercept and divide by the slope
                    .set('system:time_start', oli.get('system:time_start'));                      // ...set the output system:time_start metadata to the input image time_start otherwise it is null
        return y.toShort();                                                                       // return the image as short to match the type of the other data
        };
        exports.harmonizationRoy = harmonizationRoy;        
        """
        self.assertIsInstance(translate(text, black=False), str)

    def test_ltrend_02(self):
        """LandTrendr function"""
        text = """
        var buildSensorYearCollection = function(year, startDay, endDay, sensor, aoi, exclude){
        var startMonth = parseInt(startDay.substring(0, 2));
        var endMonth = parseInt(endDay.substring(0, 2));
        var srCollection;
        if(startMonth > endMonth){
            var oldYear = (parseInt(year)-1).toString();
            var newYear = year;
            var oldYearStartDay = startDay;
            var oldYearEndDay = '12-31';
            var newYearStartDay = '01-01';
            var newYearEndDay = endDay;            
            var oldYearCollection = filterCollection(oldYear, oldYearStartDay, oldYearEndDay, sensor, aoi);
            var newYearCollection = filterCollection(newYear, newYearStartDay, newYearEndDay, sensor, aoi);            
            srCollection = ee.ImageCollection(oldYearCollection.merge(newYearCollection));
        } else {
            srCollection = filterCollection(year, startDay, endDay, sensor, aoi);
        }
        srCollection = removeImages(srCollection, exclude)            
        return srCollection;
        };
        exports.buildSensorYearCollection = buildSensorYearCollection       
        """
        self.assertIsInstance(translate(text, black=False), str)

    def test_ltrend_03(self):
        """LandTrendr function"""
        text = """
        var getSRcollection = function(year, startDay, endDay, sensor, aoi, maskThese, exclude) {
        // make sure that mask labels are correct
        maskThese = (typeof maskThese !== 'undefined') ?  maskThese : ['cloud','shadow','snow'];
        var maskOptions = ['cloud', 'shadow', 'snow', 'water'];
        for(var i in maskThese){
            maskThese[i] =  maskThese[i].toLowerCase();
            var test = maskOptions.indexOf(maskThese[i]);
            if(test == -1){
            print('error: '+maskThese[i]+' is not included in the list maskable features. Please see ___ for list of maskable features to include in the maskThese parameter');
            return 'error';
            }
        }
        
        // get a landsat collection for given year, day range, and sensor
        var srCollection = buildSensorYearCollection(year, startDay, endDay, sensor, aoi, exclude);

        // apply the harmonization function to LC08 (if LC08), subset bands, unmask, and resample           
        srCollection = srCollection.map(function(img) {
            var dat = ee.Image(
            ee.Algorithms.If(
                sensor == 'LC08',                                                  // condition - if image is OLI
                harmonizationRoy(img.unmask()),                                    // true - then apply the L8 TO L7 alignment function after unmasking pixels that were previosuly masked (why/when are pixels masked)
                img.select(['B1', 'B2', 'B3', 'B4', 'B5', 'B7'])                   // false - else select out the reflectance bands from the non-OLI image
                .unmask()                                                       // ...unmask any previously masked pixels 
                .resample('bicubic')                                            // ...resample by bicubic 
                .set('system:time_start', img.get('system:time_start'))         // ...set the output system:time_start metadata to the input image time_start otherwise it is null
            )
            );
            
        //    // make a cloud, cloud shadow, and snow mask from fmask band
        //    var qa = img.select('pixel_qa');                                       // select out the fmask band
        //    var mask = qa.bitwiseAnd(8).eq(0).and(                                 // include shadow
        //               qa.bitwiseAnd(16).eq(0)).and(                               // include snow
        //               qa.bitwiseAnd(32).eq(0));                                   // include clouds
            
            var mask = ee.Image(1);
            if(maskThese.length !== 0){
            var qa = img.select('pixel_qa'); 
            for(var i in maskThese){
                if(maskThese[i] == 'water'){mask = qa.bitwiseAnd(4).eq(0).multiply(mask)}
                if(maskThese[i] == 'shadow'){mask = qa.bitwiseAnd(8).eq(0).multiply(mask)} 
                if(maskThese[i] == 'snow'){mask = qa.bitwiseAnd(16).eq(0).multiply(mask)}
                if(maskThese[i] == 'cloud'){mask = qa.bitwiseAnd(32).eq(0).multiply(mask)} 
            }
            return dat.mask(mask); //apply the mask - 0's in mask will be excluded from computation and set to opacity=0 in display
            } else{
            return dat;
            }
        });
        return srCollection; // return the prepared collection
        };
        exports.getSRcollection = getSRcollection;      
        """
        self.assertIsInstance(translate(text, black=False), str)

    def test_ltrend_04(self):
        """LandTrendr function"""
        text = """
        var getCombinedSRcollectionOrig = function(year, startDay, endDay, aoi, maskThese) {
            var lt5 = getSRcollection(year, startDay, endDay, 'LT05', aoi, maskThese);       // get TM collection for a given year, date range, and area
            var le7 = getSRcollection(year, startDay, endDay, 'LE07', aoi, maskThese);       // get ETM+ collection for a given year, date range, and area
            var lc8 = getSRcollection(year, startDay, endDay, 'LC08', aoi, maskThese);       // get OLI collection for a given year, date range, and area
            var mergedCollection = ee.ImageCollection(lt5.merge(le7).merge(lc8)); // merge the individual sensor collections into one imageCollection object
            return mergedCollection;                                              // return the Imagecollection
        };
        var getCombinedSRcollection = function(year, startDay, endDay, aoi, maskThese, exclude) {
            exclude = (typeof exclude !== 'undefined') ?  exclude : {}; // default to not exclude any images
            var lt5 = getSRcollection(year, startDay, endDay, 'LT05', aoi, maskThese, exclude);       // get TM collection for a given year, date range, and area
            var le7 = getSRcollection(year, startDay, endDay, 'LE07', aoi, maskThese, exclude);       // get ETM+ collection for a given year, date range, and area
            var lc8 = getSRcollection(year, startDay, endDay, 'LC08', aoi, maskThese, exclude);       // get OLI collection for a given year, date range, and area
            var mergedCollection = ee.ImageCollection(lt5.merge(le7).merge(lc8)); // merge the individual sensor collections into one imageCollection object
            //mergedCollection = removeImages(mergedCollection, exclude);
            return mergedCollection;                                              // return the Imagecollection
        };
        exports.getCombinedSRcollection = getCombinedSRcollection        
        """
        self.assertIsInstance(translate(text, black=False), str)

    def test_ltrend_05(self):
        """LandTrendr function"""
        text = """
        // make a medoid composite with equal weight among indices
        var medoidMosaic = function(inCollection, dummyCollection) {
        
        // fill in missing years with the dummy collection
        var imageCount = inCollection.toList(1).length();                                                            // get the number of images 
        var finalCollection = ee.ImageCollection(ee.Algorithms.If(imageCount.gt(0), inCollection, dummyCollection)); // if the number of images in this year is 0, then use the dummy collection, otherwise use the SR collection
        
        // calculate median across images in collection per band
        var median = finalCollection.median();                                                                       // calculate the median of the annual image collection - returns a single 6 band image - the collection median per band
        
        // calculate the different between the median and the observation per image per band
        var difFromMedian = finalCollection.map(function(img) {
            var diff = ee.Image(img).subtract(median).pow(ee.Image.constant(2));                                       // get the difference between each image/band and the corresponding band median and take to power of 2 to make negatives positive and make greater differences weight more
            return diff.reduce('sum').addBands(img);                                                                   // per image in collection, sum the powered difference across the bands - set this as the first band add the SR bands to it - now a 7 band image collection
        });
        
        // get the medoid by selecting the image pixel with the smallest difference between median and observation per band 
        return ee.ImageCollection(difFromMedian).reduce(ee.Reducer.min(7)).select([1,2,3,4,5,6], ['B1','B2','B3','B4','B5','B7']); // find the powered difference that is the least - what image object is the closest to the median of teh collection - and then subset the SR bands and name them - leave behind the powered difference band
        };      
        """
        self.assertIsInstance(translate(text, black=False), str)

    def test_ltrend_06(self):
        """LandTrendr function"""
        text = """
        //------ FUNCTION TO APPLY MEDOID COMPOSITING FUNCTION TO A COLLECTION -------------------------------------------
        var buildMosaic = function(year, startDay, endDay, aoi, dummyCollection, maskThese, exclude) {                                                                      // create a temp variable to hold the upcoming annual mosiac
        exclude = (typeof exclude !== 'undefined') ?  exclude : {}; // default to not exclude any images
        var collection = getCombinedSRcollection(year, startDay, endDay, aoi, maskThese, exclude);  // get the SR collection
        var img = medoidMosaic(collection, dummyCollection)                     // apply the medoidMosaic function to reduce the collection to single image per year by medoid 
                    .set('system:time_start', (new Date(year,8,1)).valueOf());  // add the year to each medoid image - the data is hard-coded Aug 1st 
        return ee.Image(img);                                                   // return as image object
        };


        //------ FUNCTION TO BUILD ANNUAL MOSAIC COLLECTION ------------------------------
        var buildSRcollection = function(startYear, endYear, startDay, endDay, aoi, maskThese, exclude) {
        exclude = (typeof exclude !== 'undefined') ?  exclude : {}; // default to not exclude any images
        var dummyCollection = ee.ImageCollection([ee.Image([0,0,0,0,0,0]).mask(ee.Image(0))]); // make an image collection from an image with 6 bands all set to 0 and then make them masked values
        var imgs = [];                                                                         // create empty array to fill
        for (var i = startYear; i <= endYear; i++) {                                           // for each year from hard defined start to end build medoid composite and then add to empty img array
            var tmp = buildMosaic(i, startDay, endDay, aoi, dummyCollection, maskThese, exclude);                    // build the medoid mosaic for a given year
            imgs = imgs.concat(tmp.set('system:time_start', (new Date(i,8,1)).valueOf()));       // concatenate the annual image medoid to the collection (img) and set the date of the image - hard coded to the year that is being worked on for Aug 1st
        }
        return ee.ImageCollection(imgs);                                                       // return the array img array as an image collection
        };
        exports.buildSRcollection = buildSRcollection;
        """
        # -----------------------------
        # we do not support dates yet!
        # -----------------------------
        # self.assertIsInstance(translate(text, black=False), str)

    def test_ltrend_07(self):
        """LandTrendr function"""
        text = """
        //------ FUNCTION TO RETURN A LIST OF IMAGES THAT GO INTO ANNUAL SR COMPOSITE COLLECTION ------------------------------
        function getImgID(img){return ee.String(ee.Image(img).get('system:id'));}
        function getImgIndex(img){return ee.String(ee.Image(img).get('system:index'));}


        var getCollectionIDlist = function(startYear, endYear, startDay, endDay, aoi, exclude) {
        exclude = (typeof exclude !== 'undefined') ?  exclude : {}; // default to not exclude any images
        var first = true;
        for (var i = startYear; i <= endYear; i++){
            var lt5 = buildSensorYearCollection(i, startDay, endDay, 'LT05', aoi, exclude);
            var le7 = buildSensorYearCollection(i, startDay, endDay, 'LE07', aoi, exclude);
            var lc8 = buildSensorYearCollection(i, startDay, endDay, 'LC08', aoi, exclude);
            var tmp = ee.ImageCollection(lt5.merge(le7).merge(lc8));
            if(first === true){
            var all = tmp;
            first = false;
            } else{
            all = all.merge(tmp);
            }
        }
        
        return ee.Dictionary({
            'idList':all.toList(all.size().add(1)).map(getImgID),
            'collection':all
        });
        };
        exports.getCollectionIDlist = getCollectionIDlist;
        """
        self.assertIsInstance(translate(text, black=False), str)

    def test_ltrend_08(self):
        """LandTrendr function"""
        text = """
        //------ FUNCTION TO COUNT NUMBER OF UNMASKED PIXELS IN AN INTRA ANNUAL COLLECTION ------------------------------
        var countClearViewPixels = function(intraAnnualSRcollection){
        var binary = intraAnnualSRcollection.map(function(img){
            return img.select(0)
                    .multiply(0)
                    .add(1)
                    .unmask(0);
        });
        return binary.sum();
        };
        exports.countClearViewPixels = countClearViewPixels;

        //------ FUNCTION TO BUILD ANNAUL COLLECTION OF NUMBER OF UNMASKED PIXELS AVAILABLE TO BUILD COMPOSITE ------------------------------
        var buildClearPixelCountCollection = function(startYear, endYear, startDay, endDay, aoi, maskThese) {
        var dummyCollection = ee.ImageCollection([ee.Image([0,0,0,0,0,0]).mask(ee.Image(0))]);
        var imgs = [];     
        for (var i = startYear; i <= endYear; i++) {
            var collection = getCombinedSRcollection(i, startDay, endDay, aoi, maskThese, maskThese);
            var imageCount = collection.toList(1).length();
            var finalCollection = ee.ImageCollection(ee.Algorithms.If(imageCount.gt(0), collection, dummyCollection)); 
            var notMaskCount = countClearViewPixels(finalCollection);
            imgs = imgs.concat(notMaskCount.set('system:time_start', (new Date(i,8,1)).valueOf()));      
        }
        return ee.ImageCollection(imgs);
        };
        exports.buildClearPixelCountCollection = buildClearPixelCountCollection;
        """
        # -----------------------------
        # we do not support dates yet!
        # -----------------------------
        # self.assertIsInstance(translate(text, black=False), str)

    def test_ltrend_09(self):
        """LandTrendr function"""
        text = """
        var removeImages = function(collection, exclude){
        // ["LANDSAT/LC08/C01/T1_SR/LC08_046028_20170815"](system:id) or [LC08_046028_20170815](system:index)
        // could not get (system:id) to work though, so getting via string split and slice
        if('exclude' in exclude){
            //print('in exclude')
            exclude = exclude.exclude;
            if('imgIds' in exclude){
            //print('in imgIds')
            var excludeList = exclude.imgIds;
            for(var i=0; i<excludeList.length; i++){
                //print('img blah blah')
                collection = collection.filter(ee.Filter.neq('system:index', excludeList[i].split('/').slice(-1).toString())); //system:id
            }
            }
            if('slcOff' in exclude){
            //print('in slcOff')
            if(exclude.slcOff === true){
                //print('slcOff is true')        
                collection = collection.filter(ee.Filter.and(ee.Filter.eq('SATELLITE', 'LANDSAT_7'), ee.Filter.gt('SENSING_TIME', '2003-06-01T00:00')).not());
            }
            }
        }
        return collection;
        };
        exports.removeImages = removeImages;
        """
        self.assertIsInstance(translate(text, black=False), str)

    def test_ltrend_10(self):
        """LandTrendr function"""
        text = """
        //########################################################################################################
        //##### UNPACKING LT-GEE OUTPUT STRUCTURE FUNCTIONS ##### 
        //########################################################################################################

        // ----- FUNCTION TO EXTRACT VERTICES FROM LT RESULTS AND STACK BANDS -----
        var getLTvertStack = function(lt, runParams) {
        lt = lt.select('LandTrendr');
        var emptyArray = [];                              // make empty array to hold another array whose length will vary depending on maxSegments parameter    
        var vertLabels = [];                              // make empty array to hold band names whose length will vary depending on maxSegments parameter 
        for(var i=1;i<=runParams.maxSegments+1;i++){     // loop through the maximum number of vertices in segmentation and fill empty arrays                        // define vertex number as string 
            vertLabels.push("vert_"+i.toString());               // make a band name for given vertex
            emptyArray.push(0);                             // fill in emptyArray
        }

        var zeros = ee.Image(ee.Array([emptyArray,        // make an image to fill holes in result 'LandTrendr' array where vertices found is not equal to maxSegments parameter plus 1
                                        emptyArray,
                                        emptyArray]));
        
        var lbls = [['yrs_','src_','fit_'], vertLabels,]; // labels for 2 dimensions of the array that will be cast to each other in the final step of creating the vertice output 

        var vmask = lt.arraySlice(0,3,4);           // slices out the 4th row of a 4 row x N col (N = number of years in annual stack) matrix, which identifies vertices - contains only 0s and 1s, where 1 is a vertex (referring to spectral-temporal segmentation) year and 0 is not
        
        var ltVertStack = lt.arrayMask(vmask)       // uses the sliced out isVert row as a mask to only include vertice in this data - after this a pixel will only contain as many "bands" are there are vertices for that pixel - min of 2 to max of 7. 
                            .arraySlice(0, 0, 3)          // ...from the vertOnly data subset slice out the vert year row, raw spectral row, and fitted spectral row
                            .addBands(zeros)              // ...adds the 3 row x 7 col 'zeros' matrix as a band to the vertOnly array - this is an intermediate step to the goal of filling in the vertOnly data so that there are 7 vertice slots represented in the data - right now there is a mix of lengths from 2 to 7
                            .toArray(1)                   // ...concatenates the 3 row x 7 col 'zeros' matrix band to the vertOnly data so that there are at least 7 vertice slots represented - in most cases there are now > 7 slots filled but those will be truncated in the next step
                            .arraySlice(1, 0, runParams.maxSegments+1) // ...before this line runs the array has 3 rows and between 9 and 14 cols depending on how many vertices were found during segmentation for a given pixel. this step truncates the cols at 7 (the max verts allowed) so we are left with a 3 row X 7 col array
                            .arrayFlatten(lbls, '');      // ...this takes the 2-d array and makes it 1-d by stacking the unique sets of rows and cols into bands. there will be 7 bands (vertices) for vertYear, followed by 7 bands (vertices) for rawVert, followed by 7 bands (vertices) for fittedVert, according to the 'lbls' list

        return ltVertStack;                               // return the stack
        };

        exports.getLTvertStack = getLTvertStack;
        """
        self.assertIsInstance(translate(text, black=False), str)

    def test_ltrend_11(self):
        """LandTrendr function"""
        text = """
        // #######################################################################################
        // ###### INDEX CALCULATION FUNCTIONS ####################################################
        // #######################################################################################

        // TASSELLED CAP
        var tcTransform = function(img){ 
        var b = ee.Image(img).select(["B1", "B2", "B3", "B4", "B5", "B7"]); // select the image bands
        var brt_coeffs = ee.Image.constant([0.2043, 0.4158, 0.5524, 0.5741, 0.3124, 0.2303]); // set brt coeffs - make an image object from a list of values - each of list element represents a band
        var grn_coeffs = ee.Image.constant([-0.1603, -0.2819, -0.4934, 0.7940, -0.0002, -0.1446]); // set grn coeffs - make an image object from a list of values - each of list element represents a band
        var wet_coeffs = ee.Image.constant([0.0315, 0.2021, 0.3102, 0.1594, -0.6806, -0.6109]); // set wet coeffs - make an image object from a list of values - each of list element represents a band
        
        var sum = ee.Reducer.sum(); // create a sum reducer to be applyed in the next steps of summing the TC-coef-weighted bands
        var brightness = b.multiply(brt_coeffs).reduce(sum); // multiply the image bands by the brt coef and then sum the bands
        var greenness = b.multiply(grn_coeffs).reduce(sum); // multiply the image bands by the grn coef and then sum the bands
        var wetness = b.multiply(wet_coeffs).reduce(sum); // multiply the image bands by the wet coef and then sum the bands
        var angle = (greenness.divide(brightness)).atan().multiply(180/Math.PI).multiply(100);
        var tc = brightness.addBands(greenness)
                            .addBands(wetness)
                            .addBands(angle)
                            .select([0,1,2,3], ['TCB','TCG','TCW','TCA']) //stack TCG and TCW behind TCB with .addBands, use select() to name the bands
                            .set('system:time_start', img.get('system:time_start'));
        return tc;
        };

        // NBR
        var nbrTransform = function(img) {
            var nbr = img.normalizedDifference(['B4', 'B7']) // calculate normalized difference of B4 and B7. orig was flipped: ['B7', 'B4']
                        .multiply(1000) // scale results by 1000
                        .select([0], ['NBR']) // name the band
                        .set('system:time_start', img.get('system:time_start'));
            return nbr;
        };

        // NDVI
        var ndviTransform = function(img){ 
        var ndvi = img.normalizedDifference(['B4', 'B3']) // calculate normalized dif between band 4 and band 3 (B4-B3/B4_B3)
                        .multiply(1000) // scale results by 1000
                        .select([0], ['NDVI']) // name the band
                        .set('system:time_start', img.get('system:time_start'));
        return ndvi;
        };
                        
        // NDSI
        var ndsiTransform = function(img){ 
        var ndsi = img.normalizedDifference(['B2', 'B5']) // calculate normalized dif between band 4 and band 3 (B4-B3/B4_B3)
                        .multiply(1000) // scale results by 1000
                        .select([0], ['NDSI']) // name the band
                        .set('system:time_start', img.get('system:time_start'));
        return ndsi;
        };

        // NDMI
        var ndmiTransform = function(img) {
            var ndmi = img.normalizedDifference(['B4', 'B5']) // calculate normalized difference of B4 and B7. orig was flipped: ['B7', 'B4']
                        .multiply(1000) // scale results by 1000
                        .select([0], ['NDMI']) // name the band
                        .set('system:time_start', img.get('system:time_start'));
            return ndmi;
        };

        // EVI
        var eviTransform = function(img) {
        var evi = img.expression(
            '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))', {
                'NIR': img.select('B4'),
                'RED': img.select('B3'),
                'BLUE': img.select('B1')
        })
        .multiply(1000) // scale results by 1000
        .select([0], ['EVI']) // name the band
        .set('system:time_start', img.get('system:time_start')); 
        return evi;
        };        
        """
        self.assertIsInstance(translate(text, black=False), str)

    def test_ltrend_12(self):
        """LandTrendr function"""
        text = """
        // CALCULATE A GIVEN INDEX
        var calcIndex = function(img, index, flip){
        // make sure index string in upper case
        index = index.toUpperCase();
        
        // figure out if we need to calc tc
        var tcList = ['TCB', 'TCG', 'TCW', 'TCA'];
        var doTC = tcList.indexOf(index);
        if(doTC >= 0){
            var tc = tcTransform(img);
        }
        
        // need to flip some indices if this is intended for segmentation
        var indexFlip = 1;
        if(flip == 1){
            indexFlip = -1;
        }
        
        // need to cast raw bands to float to make sure that we don't get errors regarding incompatible bands
        // ...derivations are already float because of division or multiplying by decimal
        var indexImg;
        switch (index){
            case 'B1':
            indexImg = img.select(['B1']).float();//.multiply(indexFlip);
            break;
            case 'B2':
            indexImg = img.select(['B2']).float();//.multiply(indexFlip);
            break;
            case 'B3':
            indexImg = img.select(['B3']).float();//.multiply(indexFlip);
            break;
            case 'B4':
            indexImg = img.select(['B4']).multiply(indexFlip).float();
            break;
            case 'B5':
            indexImg = img.select(['B5']).float();//.multiply(indexFlip);
            break;
            case 'B7':
            indexImg = img.select(['B7']).float();//.multiply(indexFlip);
            break;
            case 'NBR':
            indexImg = nbrTransform(img).multiply(indexFlip);
            break;
            case 'NDMI':
            indexImg = ndmiTransform(img).multiply(indexFlip);
            break;
            case 'NDVI':
            indexImg = ndviTransform(img).multiply(indexFlip);
            break;
            case 'NDSI':
            indexImg = ndsiTransform(img).multiply(indexFlip);
            break;
            case 'EVI':
            indexImg = eviTransform(img).multiply(indexFlip);
            break;
            case 'TCB':
            indexImg = tc.select(['TCB'])//.multiply(indexFlip);
            break;
            case 'TCG':
            indexImg = tc.select(['TCG']).multiply(indexFlip);
            break;
            case 'TCW':
            indexImg = tc.select(['TCW']).multiply(indexFlip);
            break;
            case 'TCA':
            indexImg = tc.select(['TCA']).multiply(indexFlip);
            break;
            default:
            print('The index you provided is not supported');
        }

        return indexImg.set('system:time_start', img.get('system:time_start'));
        };


        exports.calcIndex = calcIndex;        
        """
        # -----------------------------
        # we do not support switch yet!
        # -----------------------------
        # self.assertIsInstance(translate(text, black=False), str)

    def test_ltrend_13(self):
        """LandTrendr function"""
        text = """
        // arrange collection as an annual stack
        // TODO: would be nice to name the bands with the original band name and the year 
        var TScollectionToStack = function(collection, startYear, endYear){
        var collectionArray = collection.toArrayPerBand();
        var nBands = ee.Image(collection.first()).bandNames().getInfo().length;//;
        var bandNames = getYearBandNames(startYear, endYear);
        var allStack = ee.Image();
        for (var i = 0; i < nBands; i++){
            var bandTS = collectionArray.select([i]).arrayFlatten([bandNames]);
            allStack = ee.Image.cat([allStack, bandTS]);
        }
                            
        return allStack.slice(1,null);
        };

        exports.TScollectionToStack = TScollectionToStack;
        
        var standardize = function(collection){
        var mean = collection.reduce(ee.Reducer.mean());
        var stdDev = collection.reduce(ee.Reducer.stdDev());
        
        var meanAdj = collection.map(function(img){
            return img.subtract(mean).set('system:time_start', img.get('system:time_start'));
        });
        
        return meanAdj.map(function(img){
            return img.divide(stdDev).set('system:time_start', img.get('system:time_start'));
        });
        };        
        """
        self.assertIsInstance(translate(text, black=False), str)

    def test_ltrend_14(self):
        """LandTrendr function"""
        text = """
        // STANDARDIZE TASSELED CAP BRIGHTNESS GREENNESS WETNESS AND REDUCE THE COLLECTION
        var makeTCcomposite = function(annualSRcollection, reducer){
        var TCcomposite = annualSRcollection.map(function(img){
            var tcb = calcIndex(img, 'TCB', 1);//.unmask(0);
            var tcg = calcIndex(img, 'TCG', 1);//.unmask(0);
            var tcw = calcIndex(img, 'TCW', 1);//.unmask(0);
            return tcb.addBands(tcg)
                    .addBands(tcw)
                    .set('system:time_start', img.get('system:time_start'));
        });
        
        var tcb = TCcomposite.select(['TCB']);
        var tcg = TCcomposite.select(['TCG']);
        var tcw = TCcomposite.select(['TCW']);
            
        // standardize the TC bands
        var tcbStandard = standardize(tcb);
        var tcgStandard = standardize(tcg);
        var tcwStandard = standardize(tcw);
        
        // combine the standardized TC band collections into a single collection
        var tcStandard = tcbStandard.combine(tcgStandard).combine(tcwStandard);
        
        
        TCcomposite = tcStandard.map(function(img){
            var imgCollection = ee.ImageCollection.fromImages(
            [
                img.select(['TCB'],['Z']),
                img.select(['TCG'],['Z']),
                img.select(['TCW'],['Z'])
            ]
            );
            var reducedImg;
            switch(reducer){
            case 'mean':
                reducedImg = imgCollection.mean();
                break;
            case 'max':
                reducedImg = imgCollection.max();
                break;
            case 'sum':
                reducedImg = imgCollection.sum();
                break;
            default:
                print('The reducer you provided is not supported');
            }
            
            return reducedImg.multiply(1000).set('system:time_start', img.get('system:time_start'));            
        });                  
        return TCcomposite;
        };        
        """
        # -----------------------------
        # we do not support switch yet!
        # -----------------------------
        # self.assertIsInstance(translate(text, black=False), str)

    def test_ltrend_15(self):
        """LandTrendr function"""
        text = """
        // STANDARDIZE B5, TCB, TCG, NBR AND REDUCE THE COLLECTION
        var makeEnsemblecomposite1 = function(annualSRcollection, reducer){
        // make a collection of the ensemble indices stacked as bands
        var TCcomposite = annualSRcollection.map(function(img){
            var b5   = calcIndex(img, 'B5', 1);
            var tcb  = calcIndex(img, 'TCB', 1);
            var tcg  = calcIndex(img, 'TCG', 1);
            var nbr  = calcIndex(img, 'NBR', 1);
            return b5.addBands(tcb)
                    .addBands(tcg)
                    .addBands(nbr)
                    .set('system:time_start', img.get('system:time_start'));
        });
        
        // make subset collections of each index
        var b5 = TCcomposite.select('B5');
        var tcb = TCcomposite.select('TCB');
        var tcg = TCcomposite.select('TCG');
        var nbr = TCcomposite.select('NBR');
            
        // standardize each index - get z-score
        var b5Standard = standardize(b5);
        var tcbStandard = standardize(tcb);
        var tcgStandard = standardize(tcg);
        var nbrStandard = standardize(nbr);
            
        // combine the standardized TC band collections into a single collection
        var tcStandard = b5Standard.combine(tcbStandard).combine(tcgStandard).combine(nbrStandard);
        
        // reduce the collection to a single value
        TCcomposite = tcStandard.map(function(img){
            var imgCollection = ee.ImageCollection.fromImages(
            [
                img.select(['B5'],['Z']),//.pow(ee.Image(1)).multiply(img.select('B5').gte(0).where(img.select('B5').lt(0),-1)),
                img.select(['TCB'],['Z']),//.pow(ee.Image(1.5)).multiply(img.select('TCB').gte(0).where(img.select('TCB').lt(0),-1)),
                img.select(['TCG'],['Z']),//.pow(ee.Image(1.5)).multiply(img.select('TCG').gte(0).where(img.select('TCG').lt(0),-1)),
                img.select(['NBR'],['Z'])//.pow(ee.Image(1.5)).multiply(img.select('NBR').gte(0).where(img.select('NBR').lt(0),-1))
            ]
            );
            var reducedImg;
            switch(reducer){
            case 'mean':
                reducedImg = imgCollection.mean();
                break;
            case 'max':
                reducedImg = imgCollection.max();
                break;
            case 'sum':
                reducedImg = imgCollection.sum();
                break;
            default:
                print('The reducer you provided is not supported');
            }
            
            return reducedImg.multiply(1000).set('system:time_start', img.get('system:time_start'));            
        });  
        
        return TCcomposite;
        };        
        """
        # -----------------------------
        # we do not support switch yet!
        # -----------------------------
        # self.assertIsInstance(translate(text, black=False), str)

    def test_ltrend_16(self):
        """LandTrendr function"""
        text = """
        // THIS BUILDS AN ANNUAL-SR-TRANSFORMED COLLECTION FOR USE BY TIMESYNC-LEGACY
        var buildTSindexCollection = function(collection, ftvList){
        return collection.map(function(img){
                    var allStack = ee.Image();
                    var ftvimg;
                    for(var ftv in ftvList){
                    ftvimg = calcIndex(img, ftvList[ftv], 0)
                                        .select([ftvList[ftv]],['ftv_'+ftvList[ftv].toLowerCase()])
                                        .unmask(0);
            
                        allStack = allStack.addBands(ftvimg)
                                        .set('system:time_start', img.get('system:time_start'));
                    }
                    return allStack.slice(1,null);
                });
        };
        // TRANSFORM AN ANNUAL SR COLLECTION TO AN ANNUAL COLLECTION OF SELECTED INDICES OR BANDS
        var transformSRcollection = function(srCollection, bandList){
        return srCollection.map(function(img){
            var allStack = calcIndex(img, bandList[0], 0);
            for(var band=1; band < bandList.length; band++){
            var bandImg = calcIndex(img, bandList[band], 0);
            allStack = allStack.addBands(bandImg);
            }
            return allStack.set('system:time_start', img.get('system:time_start'));
        });
        };

        exports.transformSRcollection = transformSRcollection;        
        """
        self.assertIsInstance(translate(text, black=False), str)

    def test_ltrend_17(self):
        """LandTrendr function"""
        text = """
        exports.runLT = function(startYear, endYear, startDay, endDay, aoi, index, ftvList, runParams, maskThese, exclude){
        maskThese = (typeof maskThese !== 'undefined') ?  maskThese : ['cloud','shadow','snow'];
        exclude = (typeof exclude !== 'undefined') ?  exclude : {}; // default to not exclude any images
        var annualSRcollection = buildSRcollection(startYear, endYear, startDay, endDay, aoi, maskThese, exclude); // Peter here, I think this collects surface reflectance images 
        var annualLTcollection = buildLTcollection(annualSRcollection, index, ftvList); 
        runParams.timeSeries = annualLTcollection;
        return ee.Algorithms.TemporalSegmentation.LandTrendr(runParams);
        };


        // TODO: update the ftv parameter in the guide
        var getFittedData = function(lt, startYear, endYear, index, ftv){
        var bandNames = getYearBandNames(startYear, endYear);
        var search;
        if(ftv === true){
            search = index.toUpperCase()+'_fit';
        } else {
            search = 'ftv_'+index.toLowerCase()+'_fit';
        }
        return lt.select(search)
                .arrayFlatten([bandNames]);
        };

        exports.getFittedData = getFittedData;

        // MAKE RGB COMPOSITE
        var makeRGBcomposite = function(index, startYear, endYear, startDay, endDay, redYear, greenYear, blueYear, aoi, runParams, nStdev, maskThese, exclude){
        maskThese = (typeof maskThese !== 'undefined') ?  maskThese : ['cloud','shadow','snow'];
        exclude = (typeof exclude !== 'undefined') ?  exclude : {}; // default to not exclude any images
        var annualSRcollection = buildSRcollection(startYear, endYear, startDay, endDay, aoi, maskThese, exclude);
        var annualLTcollection = buildLTcollection(annualSRcollection, index, [index]);
        runParams.timeSeries = annualLTcollection;
        var lt = ee.Algorithms.TemporalSegmentation.LandTrendr(runParams);
        var ftvStack = getFittedData(lt, startYear, endYear, index);
        return ftvStack.select(["yr_"+redYear.toString(),"yr_"+greenYear.toString(),"yr_"+blueYear.toString()]); 
        };
        exports.makeRGBcomposite = makeRGBcomposite;
        """
        self.assertIsInstance(translate(text, black=False), str)

    def test_ltrend_18(self):
        """LandTrendr function"""
        text = """
        exports.mapRGBcomposite = function(index, startYear, endYear, startDay, endDay, redYear, greenYear, blueYear, aoi, runParams, nStdev, maskThese, exclude){
        maskThese = (typeof maskThese !== 'undefined') ?  maskThese : ['cloud','shadow','snow'];
        exclude = (typeof exclude !== 'undefined') ?  exclude : {}; // default to not exclude any images
        var rgb = makeRGBcomposite(index, startYear, endYear, startDay, endDay, redYear, greenYear, blueYear, aoi, runParams, nStdev, maskThese, exclude);
        var stretch = stdDevStretch(rgb, aoi, nStdev);
        var rgbVis = rgb.visualize({min: stretch[0], max: stretch[1], gamma: 1}).clip(aoi); 
        return rgbVis;
        //Map.centerObject(aoi, 10);
        //Map.addLayer(rgbVis);
        };


        // GENERIC FLATTEN COLLECTION INTO BAND STACK
        var collectionToBandStack = function(collection, startYear, endYear, maskFill){
        maskFill = (typeof maskFill !== 'undefined') ?  maskFill : 0;
        var unmaskedCollection = collection.map(function(img){
            return img.unmask(maskFill);
        });
        var collectionArray = unmaskedCollection.toArrayPerBand();
        var nBands = unmaskedCollection.first().bandNames().length().getInfo();
        var years = [];
        var allStack = ee.Image();
        for (var i = startYear; i <= endYear; ++i) years.push(i.toString());
        for (i = 0; i < nBands; i++){
            var bandTS = collectionArray.select([i]).arrayFlatten([years]);
            allStack = ee.Image.cat([allStack, bandTS]);
        }    
        return allStack.slice(1,null).toShort();     
        };
        exports.collectionToBandStack = collectionToBandStack;



        // FLATTEN SOURCE COLLECTION INTO A GIANT STACK FOR EXPORT - USED BY TIMESYNC
        exports.timesyncLegacyStack = function(startYear, endYear, startDay, endDay, aoi, maskThese, exclude){
        exclude = (typeof exclude !== 'undefined') ?  exclude : {}; // default to not exclude any images
        var annualSRcollection = buildSRcollection(startYear, endYear, startDay, endDay, aoi, maskThese);
        var annualTScollection = buildTSindexCollection(annualSRcollection, ['B1','B2','B3','B4','B5','B7','TCB','TCG','TCW']);
        
        // THE FOLLOWING COULD BE A GENERIC FUNCTION
        var annualTSArray = annualTScollection.toArrayPerBand();
        var years = [];
        var allStack = ee.Image();
        for (var i = startYear; i <= endYear; ++i) years.push(i.toString());
        for (i = 0; i <= 8; i++){
            var bandTS = annualTSArray.select([i]).arrayFlatten([years]);
            allStack = ee.Image.cat([allStack, bandTS]);
        }
                            
        return allStack.slice(1,null).toShort();
        //////////////////////////////////////////////  
        };

        // RETURN THE SEGMENT COUNT
        var getSegmentCount = function(segData) {
        return segData.arrayLength(1).select([0],['segCount']).toByte();
        };
        exports.getSegmentCount = getSegmentCount;
        """
        self.assertIsInstance(translate(text, black=False), str)

    def test_ltrend_19(self):
        """LandTrendr function"""
        text = """
        // RETURN THE SEGMENT INFORMATION AS A DICTIONARY
        var getSegmentDictionary = function(lt, options) {
        
        // create a default options dictionary, if one is not provided
        options = (typeof options !== 'undefined') ?  options : {
            right: false,
            index: null
        };
        
        // slice out variables 
        var ltlt = lt.select('LandTrendr');              // select the LandTrendr band
        var rmse = lt.select('rmse');                    // select the rmse band
        var vertexMask = ltlt.arraySlice(0, 3, 4);       // slice out the 'Is Vertex' row - yes(1)/no(0)
        var vertices = ltlt.arrayMask(vertexMask);       // use the 'Is Vertex' row as a mask for all rows
        var leftList = vertices.arraySlice(1, 0, -1);    // slice out the vertices as the start of segments
        var rightList = vertices.arraySlice(1, 1, null); // slice out the vertices as the end of segments
        var startYear = leftList.arraySlice(0, 0, 1);    // get year dimension of LT data from the segment start vertices
        var startVal = leftList.arraySlice(0, 2, 3);     // get spectral index dimension of LT data from the segment start vertices
        var endYear = rightList.arraySlice(0, 0, 1);     // get year dimension of LT data from the segment end vertices 
        var endVal = rightList.arraySlice(0, 2, 3);      // get spectral index dimension of LT data from the segment end vertices
        var dur = endYear.subtract(startYear);           // subtract the segment start year from the segment end year to calculate the duration of segments 
        
        // flip spectral values over if requested
        if(options.right === true){
            if(indexFlipper(options.index) == -1){
            print('Negative delta is disturbance')
            startVal = startVal.multiply(-1);
            endVal = endVal.multiply(-1);
            } else{print('Postive delta is disturbance')}
        } else{print('Postive delta is disturbance')}
        
        // create delta variables 
        var mag = endVal.subtract(startVal);         // substract the segment start index value from the segment end index value to calculate the delta of segments
        var rate = mag.divide(dur);                  // calculate the rate of spectral change    
        var dsnr = mag.divide(rmse);                 // make mag relative to fit rmse
        
        // return segment info as a dictionary
        return {
            startYear:startYear,
            startVal:startVal,
            endYear:endYear,
            endVal:endVal,
            dur:dur,
            mag:mag,
            rate:rate,
            dsnr:dsnr,
        };
        };
        exports.getSegmentDictionary = getSegmentDictionary;


        // RETURN THE SEGMENT INFORMATION AS AN ARRAY
        var getSegmentArray = function(lt, options) {
        
        // create a default options dictionary, if one is not provided
        options = (typeof options !== 'undefined') ?  options : {
            right: false,
            index: null
        };
        
        // seg the segment information as a dictionary
        var segInfo = getSegmentDictionary(lt, options);
        
        // format the segment information dictionary as an array
        return ee.Image.cat([
            segInfo.startYear,//.unmask(ee.Image(ee.Array([[-9999]]))),
            segInfo.endYear,//.unmask(ee.Image(ee.Array([[-9999]]))),
            segInfo.startVal,//.unmask(ee.Image(ee.Array([[-9999]]))),
            segInfo.endVal,//.unmask(ee.Image(ee.Array([[-9999]]))),
            segInfo.mag,//.unmask(ee.Image(ee.Array([[-9999]]))),
            segInfo.dur,//.unmask(ee.Image(ee.Array([[-9999]]))),
            segInfo.rate,//.unmask(ee.Image(ee.Array([[-9999]]))),
            segInfo.dsnr,//.unmask(ee.Image(ee.Array([[-9999]])))
            ]).toArray(0); 
        
        };
        exports.getSegmentArray = getSegmentArray;        
        """
        self.assertIsInstance(translate(text, black=False), str)

    def test_ltrend_20(self):
        """LandTrendr function"""
        text = """
        // #######################################################################################
        // ###### PIXEL TIME SERIES FUNCTIONS ####################################################
        // #######################################################################################

        // RETURN IMAGE BAND VALUES FOR A SINGLE PIXEL AS AN OBJECT
        var getPixelInfo = function(img, pixel) {
        return img.unmask(-9999).reduceRegion({
        reducer: 'first',
        geometry: pixel,
        scale: 30
        }).getInfo();
        };
        exports.getPixelInfo = getPixelInfo;

        // RETURN LT RESULTS FOR A SINGLE PIXEL AS AN OBJECT
        var ltPixelTimeSeries = function(img, pixel) {
        return img.reduceRegion({
        reducer: 'first',
        geometry: pixel,
        scale: 30
        }).getInfo();
        };
        exports.ltPixelTimeSeries = ltPixelTimeSeries;

        // PARSE OBJECT RETURNED FROM 'getPoint' TO ARRAY OF SOURCE AND FITTED
        exports.ltPixelTimeSeriesArray = function(lt, pixel, indexFlip){
        var pixelTS = ltPixelTimeSeries(lt, pixel);
        if(pixelTS.LandTrendr === null){pixelTS.LandTrendr = [[0,0],[0,0],[0,0]]}
        var data = [['Year', 'Original', 'Fitted']];
        var len = pixelTS.LandTrendr[0].length;
        for (var i = 0; i < len; i++) {
            data = data.concat([[pixelTS.LandTrendr[0][i], pixelTS.LandTrendr[1][i]*indexFlip, pixelTS.LandTrendr[2][i]*indexFlip]]);
        }
        return {ts:data, rmse:pixelTS.rmse};
        };
        """
        self.assertIsInstance(translate(text, black=False), str)

    def test_ltrend_21(self):
        """LandTrendr function"""
        text = """
        // #######################################################################################
        // ###### LT ARRAY FUNCTIONS ###############################################################
        // #######################################################################################

        // get segment info array
        var getSegmentData = function(lt, index, delta, options){
        // Deal with options.
        var _options = {right: false};  // Defaults
        if (typeof options == 'boolean') {
            _options.right = options;
        }
        
        var ltlt = lt.select('LandTrendr');            // select the LandTrendr band
        var rmse = lt.select('rmse');                  // select the rmse band
        var vertexMask = ltlt.arraySlice(0, 3, 4);     // slice out the 'Is Vertex' row - yes(1)/no(0)
        var vertices = ltlt.arrayMask(vertexMask);     // use the 'Is Vertex' row as a mask for all rows
        var leftList = vertices.arraySlice(1, 0, -1);    // slice out the vertices as the start of segments
        var rightList = vertices.arraySlice(1, 1, null); // slice out the vertices as the end of segments
        var startYear = leftList.arraySlice(0, 0, 1);    // get year dimension of LT data from the segment start vertices
        var startVal = leftList.arraySlice(0, 2, 3);     // get spectral index dimension of LT data from the segment start vertices
        var endYear = rightList.arraySlice(0, 0, 1);     // get year dimension of LT data from the segment end vertices 
        var endVal = rightList.arraySlice(0, 2, 3);      // get spectral index dimension of LT data from the segment end vertices
        var dur = endYear.subtract(startYear);       // subtract the segment start year from the segment end year to calculate the duration of segments 
        var mag = endVal.subtract(startVal);         // substract the segment start index value from the segment end index value to calculate the delta of segments
        var rate = mag.divide(dur);                  // calculate the rate of spectral change    
        var dsnr = mag.divide(rmse);              // make mag relative to fit rmse
        
        // whether to return all segments or either dist or grow
        if(delta.toLowerCase() == 'all'){
            // if the data should be set to the correct orientation, adjust it - don't need to do this for either gain or loss mag/rate/dsnr because it is set to absolute
            if(_options.right === true){
            if(indexFlipper(index) == -1){
                startVal = startVal.multiply(-1);
                endVal = endVal.multiply(-1);
                mag = mag.multiply(-1);
                rate = rate.multiply(-1);
                dsnr = dsnr.multiply(-1);
            }
            }
            // now just get out - return the result 
            return ee.Image.cat([startYear, endYear, startVal, endVal, mag, dur, rate, dsnr])
                        //.unmask(ee.Image(ee.Array([[-9999],[-9999],[-9999],[-9999],[-9999],[-9999],[-9999],[-9999]])))
                        .unmask(ee.Image(ee.Array([[-9999]])))
                        .toArray(0);
        } else if((delta.toLowerCase() == 'gain') || (delta.toLowerCase() == 'loss')){
            var changeTypeMask;
            if(delta.toLowerCase() == 'gain'){
            changeTypeMask = mag.lt(0);
            } else if(delta.toLowerCase() == 'loss'){
            changeTypeMask = mag.gt(0);
            }
        
            var flip = indexFlipper(index);  
            return ee.Image.cat([
                startYear.arrayMask(changeTypeMask),//.unmask(ee.Image(ee.Array([[-9999]]))),
                endYear.arrayMask(changeTypeMask),//.unmask(ee.Image(ee.Array([[-9999]]))),
                startVal.arrayMask(changeTypeMask).multiply(flip),//.unmask(ee.Image(ee.Array([[-9999]]))),
                endVal.arrayMask(changeTypeMask).multiply(flip),//.unmask(ee.Image(ee.Array([[-9999]]))),
                mag.arrayMask(changeTypeMask).abs(),//.unmask(ee.Image(ee.Array([[-9999]]))),
                dur.arrayMask(changeTypeMask),//.unmask(ee.Image(ee.Array([[-9999]]))),
                rate.arrayMask(changeTypeMask).abs(),//.unmask(ee.Image(ee.Array([[-9999]]))),
                dsnr.arrayMask(changeTypeMask).abs(),//.unmask(ee.Image(ee.Array([[-9999]])))
            ])
            //.unmask(ee.Image(ee.Array([[-9999],[-9999],[-9999],[-9999],[-9999],[-9999],[-9999],[-9999]])))
            .unmask(ee.Image(ee.Array([[-9999]])))
            .toArray(0); 
        }        
        };
        exports.getSegmentData = getSegmentData;



        // #######################################################################################
        // ###### HELPER FUNCTIONS ###############################################################
        // #######################################################################################

        // GET A SERIES OF BANDS NAMES AS YEARS
        var getYearBandNames = function(startYear, endYear){
        var years = [];                                                           // make an empty array to hold year band names
        for (var i = startYear; i <= endYear; ++i) years.push("yr_"+i.toString()); // fill the array with years from the startYear to the endYear and convert them to string
        return years;
        };
        exports.getYearBandNames = getYearBandNames;        
        """
        self.assertIsInstance(translate(text, black=False), str)

    def test_ltrend_22(self):
        """LandTrendr function"""
        text = """
        // STANDARD DEVIATION STRETCH
        var stdDevStretch = function(img, aoi, nStdev){
        var mean = img.reduceRegion({reducer:ee.Reducer.mean(), geometry:aoi, scale:900, bestEffort:true, maxPixels:1e4})
                    .toArray()
                    .reduce(ee.Reducer.mean(), [0]);

        var stdDev = img.reduceRegion({reducer:ee.Reducer.stdDev(), geometry:aoi, scale:900, bestEffort:true, maxPixels:1e4})
                        .toArray()
                        .reduce(ee.Reducer.mean(), [0])
                        .multiply(nStdev);

        var max = mean.add(stdDev).getInfo()[0];
        var min = mean.subtract(stdDev).getInfo()[0];
        return [min, max];
        };

        // INDEX FLIPPER
        var indexFlipper = function(index){
        var indexObj = {
            'NBR': -1,
            'NDVI': -1,
            'NDSI': -1,  // ???? this is a tricky one
            'NDMI': -1,
            'EVI': -1,  
            'TCB': 1,
            'TCG': -1,
            'TCW': -1,
            'TCA': -1,
            'B1': 1,
            'B2': 1,
            'B3': 1,
            'B4': -1,
            'B5': 1,
            'B7': 1,
            'ENC': 1,
            'ENC1': 1,
            'TCC': 1,  
            'NBRz': 1,
            'B5z': 1
        };
        return indexObj[index];
        };
        exports.indexFlipper = indexFlipper;


        var makeBoolean = function(value){
        if(typeof(value) !== "boolean"){
            value = value.toLowerCase() != 'false';
        }
        return value;
        };
        exports.makeBoolean = makeBoolean;



        var getFittedRGBcol = function(lt, startYear, endYear, bands, visParams){
        var r = getFittedData(lt, startYear, endYear, bands[0]);
        var g = getFittedData(lt, startYear, endYear, bands[1]);
        var b = getFittedData(lt, startYear, endYear, bands[2]);
        var yearsStr = ee.List(getYearBandNames(startYear, endYear))
        var rgbList = yearsStr.map(function(year){
            return r.select([year]).addBands(g.select([year])).addBands(b.select([year])).rename(['R', 'G', 'B']);
        });
        var rgbCol = ee.ImageCollection(rgbList.flatten()).map(function(img){
            return img.visualize(visParams);
        }).map(function(img){
            var year = ee.Number.parse(img.get('system:index')).add(startYear);
            return img.set({'system:time_start': ee.Date.fromYMD(year, 1, 1).millis(), 'composite_year':year});
        });
        return rgbCol;
        };
        exports.getFittedRGBcol = getFittedRGBcol;
        """
        # Not solved yet!
        # self.assertIsInstance(translate(text, black=False), str)

    def test_ltrend_23(self):
        """LandTrendr function"""
        text = """
        // #######################################################################################
        // ###### UI STUFF #######################################################################
        // #######################################################################################

        // LT PARAMS
        exports.paramPanel = function(){

        var runParams = [
        {label: 'Max Segments:', value: 6},
        {label: 'Spike Threshold:', value: 0.9},
        {label: 'Vertex Count Overshoot:', value: 3},
        {label: 'Prevent One Year Recovery:', value: true},
        {label: 'Recovery Threshold:', value: 0.25},
        {label: 'p-value Threshold:', value: 0.05},
        {label: 'Best Model Proportion:', value: 0.75},
        {label: 'Min Observations Needed:', value: 6},
        ];

        var paramBoxes = [];
        var paramPanels = [ui.Label('Define Segmentation Parameters',{fontWeight: 'bold'})];
        runParams.forEach(function(param, index){
        var paramLabel = ui.Label(param.label);
        var paramBox = ui.Textbox({value:param.value});
        paramBox.style().set('stretch', 'horizontal');
        var paramPanel = ui.Panel([paramLabel,paramBox], ui.Panel.Layout.Flow('horizontal'));
        paramBoxes.push(paramBox);
        paramPanels.push(paramPanel);
        });

        return ui.Panel(paramPanels, null, {stretch: 'horizontal'});
        };

        exports.getParams = function(paramPanel){
        var prevOneYrRec = paramPanel.widgets().get(4).widgets().get(1).getValue();
        
        prevOneYrRec = makeBoolean(prevOneYrRec);
        
        //if(typeof(prevOneYrRec) !== "boolean"){
        //  prevOneYrRec = prevOneYrRec.toLowerCase() != 'false';
        //}
        
        return { 
            maxSegments:              parseInt(paramPanel.widgets().get(1).widgets().get(1).getValue()),
            spikeThreshold:         parseFloat(paramPanel.widgets().get(2).widgets().get(1).getValue()),
            vertexCountOvershoot:     parseInt(paramPanel.widgets().get(3).widgets().get(1).getValue()),
            preventOneYearRecovery:                                                        prevOneYrRec,
            recoveryThreshold:      parseFloat(paramPanel.widgets().get(5).widgets().get(1).getValue()),
            pvalThreshold:          parseFloat(paramPanel.widgets().get(6).widgets().get(1).getValue()),
            bestModelProportion:    parseFloat(paramPanel.widgets().get(7).widgets().get(1).getValue()),
            minObservationsNeeded:    parseInt(paramPanel.widgets().get(8).widgets().get(1).getValue())
        };
        };
        """
        # ui should show a warning
        # self.assertIsInstance(translate(text, black=False), str)


if __name__ == "__main__":
    unittest.main()
