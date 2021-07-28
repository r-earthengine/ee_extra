var utils = require("users/aazuspan/geeSharp:utils.js");

/**
 * Sharpen an image using Brovey sharpening, where each band is calculated
 * based on a weighted intensity band and the panchromatic band.
 * @param {ee.Image} img An image to sharpen. All bands should spectrally
 *  overlap the panchromatic band to avoid spectral distortion.
 * @param {ee.Image} pan An single-band panchromatic image.
 * @param {ee.List} weights A list of weights to apply to each band. If
 *  missing, equal weights will be used.
 * @return {ee.Image} The input image with all bands sharpened to the spatial
 *  resolution of the panchromatic band.
 */
exports.sharpen = function (img, pan, weights) {
  var panProj = pan.projection();

  // If any weights are missing, use equal weights
  if (utils.isMissing(weights)) {
    var bandNum = img.bandNames().length();
    var bandWeight = ee.Number(1).divide(bandNum);
    weights = ee.List.repeat(bandWeight, bandNum);
  }

  // Calculate intensity band as sum of the weighted visible bands
  var intensity = utils.calculateWeightedIntensity(img, weights);
  // Resample the intensity band
  var intensitySharp = intensity.resample().reproject(panProj);

  var imgBrovey = img.resample("bilinear").reproject(panProj);
  imgBrovey = imgBrovey.divide(intensitySharp).multiply(pan);

  return imgBrovey;
};
