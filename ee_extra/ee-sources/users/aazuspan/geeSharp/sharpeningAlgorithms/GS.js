var utils = require("users/aazuspan/geeSharp:utils.js");

/**
 * Calculate the next Gram-Schmidt transformed image given a list of previous
 * Gram-Schmidt transformed images. See Equation 1 of Hallabia et al 2014.
 * @param {ee.Image} ms A multispectral image.
 * @param {ee.List} gsList A list of Gram-Schmidt transformed images.
 */
function calculateGs(ms, gsList) {
  // Get the reduction parameters which are passed through the gsList
  var reductionParameters = ee.List(ee.List(gsList).get(0));

  // Unpack the parameters
  var geometry = reductionParameters.get(0);
  var scale = reductionParameters.get(1);
  var maxPixels = reductionParameters.get(2);

  // Get the previous GS as the last element
  var previous = ee.Image(ee.List(gsList).get(-1));

  // Calculate coefficient g between MS and previous GS
  var g = calculateGsCoefficient(ms, previous, geometry, scale, maxPixels);
  var gsNew = ms.subtract(g);

  // Return the list with the new GS image added
  return ee.List(gsList).add(gsNew);
}

/**
 * Calculate the Gram-Schmidt coefficient g. See Equation 2 in Hallabia et al
 * 2014.
 * @param {ee.Image} ms A multispectral image.
 * @param {ee.Image} gs A Gram-Schmidt transformed image.
 * @param {ee.Geometry} geometry The region to calculate image
 *  statistics for. Sharpening will only be accurate within this region.
 * @param {ee.Number} scale The scale, in projection units, to
 *  calculate image statistics at.
 * @param {ee.Number} maxPixels The maximum number of pixels to sample when
 *  calculating image statistics
 * @return {ee.Image} A constant GS coefficient.
 */
function calculateGsCoefficient(ms, gs, geometry, scale, maxPixels) {
  var imgArray = ee.Image.cat(ms, gs).toArray();

  var covarMatrix = imgArray.reduceRegion({
    reducer: ee.Reducer.covariance(),
    geometry: geometry,
    scale: scale,
    maxPixels: maxPixels,
  });

  var covarArray = ee.Array(covarMatrix.get("array"));

  var covar = covarArray.get([0, 1]);
  var variance = covarArray.get([1, 1]);

  var g = covar.divide(variance);

  return ee.Image.constant(g);
}

/**
 * Sharpen all bands of an image using the Gram-Schmidt orthonormalization
 * process, following Hallabia et al 2014.
 * @param {ee.Image} img An image to sharpen.
 * @param {ee.Image} pan An single-band panchromatic image.
 * @param {ee.Geometry, default null} geometry The region to calculate image
 *  statistics for. Sharpening will only be accurate within this region.
 * @param {ee.Number, default null} scale The scale, in projection units, to
 *  calculate image statistics at.
 * @param {ee.Number, default 1000000000000} maxPixels The maximum number of
 *  pixels to sample when calculating image statistics.
 * @return {ee.Image} The input image with all bands sharpened to the spatial
 *  resolution of the panchromatic band.
 */
exports.sharpen = function (img, pan, geometry, scale, maxPixels) {
  // Params passed through iterate need to be explicitly set to null or else
  // GEE serialization will fail
  if (utils.isMissing(geometry)) {
    geometry = null;
  }

  if (utils.isMissing(scale)) {
    scale = null;
  }

  if (utils.isMissing(maxPixels)) {
    maxPixels = 1e12;
  }

  // Resample multispectral bands to pan resolution
  img = img.resample("bilinear").reproject({
    crs: pan.projection(),
    scale: pan.projection().nominalScale(),
  });

  // Calculate panSim as a mean of the MS bands
  var panSim = img.reduce(ee.Reducer.mean()).clip(img.geometry());

  // The reduction parameters to be passed to calculateGs
  var reductionParameters = [geometry, scale, maxPixels];

  // GS1 image is the panSim. Including the reduction parameters here is awful,
  // but the only way to pass them to calculateGs via iterate.
  var gsList = ee.List([reductionParameters, panSim]);

  // Convert the multispectral bands to an image collection so that it can be
  // iterated over
  var msCollection = utils.multibandToCollection(img);

  // Iterate over the MS collection, calculating GS bands. Slice to remove the
  // reduction parameters.
  var gsCollection = ee.ImageCollection(
    ee.List(msCollection.iterate(calculateGs, gsList)).slice(1)
  );

  // Convert the GS collection to a multiband image
  var gsBands = gsCollection.toBands();

  // Histogram match the pan band to the simulated pan band
  var panMatch = utils.linearHistogramMatch(
    pan,
    panSim,
    geometry,
    scale,
    maxPixels
  );

  // Swap the matched pan band for the first GS band
  gsBands = ee.Image.cat(panMatch, gsBands.slice(1));

  // Spatial detail is the difference between the matched pan band and the simulated pan band
  var detail = panMatch.subtract(panSim);

  // Convert GS bands to an image collection so that it can be mapped over
  var gsBandImages = utils.multibandToCollection(gsBands);

  // Calculate constant g coefficients for each gsBand
  var gCoefficients = gsBandImages.map(function (x) {
    return calculateGsCoefficient(x, panSim, geometry, scale, maxPixels);
  });

  // Sharpen the multispectral bands using g coefficients and pan detail
  var sharpBands = img.add(gCoefficients.toBands().slice(1).multiply(detail));

  return sharpBands;
};
