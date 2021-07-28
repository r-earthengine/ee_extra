var utils = require("users/aazuspan/geeSharp:utils.js");

/**
 * Sharpen all bands of an image by converting it to principal components,
 * rescaling a panchromatic band to match the first principal component,
 * swapping the high-resolution panchromatic band for the first principal
 * component, and inverting the transformation to create a high-resolution
 * multispectral image.
 * @param {ee.Image} img An image to sharpen.
 * @param {ee.Image} pan An single-band panchromatic image.
 * @param {number, default 1} substitutePC The number of the principal
 * component to replace with the pan band. Must be in range 1 - n, where n is
 * the number of bands in the input image.
 * @param {ee.Geometry, default null} geometry The region to calculate image
 *  statistics for. Sharpening will only be accurate within this region.
 * @param {ee.Number, default null} scale The scale, in projection units, to
 *  calculate image statistics at.
 * @param {ee.Number, default 1000000000000} maxPixels The maximum number of
 *  pixels to sample when calculating image statistics
 * @return {ee.Image} The input image with all bands sharpened to the spatial
 *  resolution of the panchromatic band.
 */
exports.sharpen = function (
  img,
  pan,
  substitutePC,
  geometry,
  scale,
  maxPixels
) {
  // Default to substituting the first PC
  if (utils.isMissing(substitutePC)) {
    substitutePC = 1;
  }

  if (utils.isMissing(maxPixels)) {
    maxPixels = 1e12;
  }

  // Resample the image to the panchromatic resolution
  img = img.resample("bilinear");
  img = img.reproject(pan.projection());

  // Store band names for future use
  var bandNames = img.bandNames();
  var panBand = pan.bandNames().get(0);

  // Mean-center the images to allow efficient covariance calculation
  var imgMean = utils.reduceImage(
    img,
    ee.Reducer.mean(),
    geometry,
    scale,
    maxPixels
  );

  var imgCentered = img.subtract(imgMean);

  // Convert image to 1D array
  var imgArray = imgCentered.toArray();

  // Calculate a covariance matrix between all bands
  var covar = imgArray.reduceRegion({
    reducer: ee.Reducer.centeredCovariance(),
    geometry: geometry,
    scale: scale,
    maxPixels: maxPixels,
  });

  // Pull out the covariance results as an array
  var covarArray = ee.Array(covar.get("array"));

  // Calculate eigenvalues and eigenvectors
  var eigens = covarArray.eigen();

  // Pull out eigenvectors (elements after eigenvalues in each list) [7x7]
  var eigenVectors = eigens.slice(1, 1);

  // Convert image to 2D array
  var imgArray2d = imgArray.toArray(1);

  // Build the names of the principal component bands
  var pcSeq = ee.List.sequence(1, bandNames.length());
  var pcNames = pcSeq.map(function (x) {
    return ee.String("PC").cat(ee.Number(x).int());
  });

  var principalComponents = ee
    .Image(eigenVectors)
    .matrixMultiply(imgArray2d)
    // Flatten unnecessary dimension
    .arrayProject([0])
    // Split into a multiband image
    .arrayFlatten([pcNames]);

  // Rescale the pan band to more closely match the substituted PC
  pan = utils.linearHistogramMatch(
    pan,
    principalComponents.select(substitutePC - 1),
    geometry,
    scale,
    maxPixels
  );

  // Build the band list, swapping the pan band for the appropriate PC
  var sharpenBands = pcNames.set(substitutePC - 1, panBand);

  principalComponents = principalComponents.addBands(pan);
  principalComponents = principalComponents.select(sharpenBands);

  // Undo the PC transformation
  var reconstructedCentered = ee
    .Image(eigenVectors)
    .matrixSolve(principalComponents.toArray().toArray(1))
    .arrayProject([0])
    .arrayFlatten([bandNames]);

  // Undo the mean-centering
  var reconstructed = reconstructedCentered.add(imgMean);

  return reconstructed;
};
