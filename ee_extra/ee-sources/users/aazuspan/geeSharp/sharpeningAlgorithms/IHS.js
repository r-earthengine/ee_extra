/**
 * Sharpen all bands of an image using IHS, where RGB bands are converted to
 * IHS and the intensity data is swapped for the panchromatic band.
 * @param {ee.Image} img An image to sharpen. To work correctly, the image must
 * have 3 bands: red, green, and blue.
 * @param {ee.Image} pan An single-band panchromatic image.
 * @return {ee.Image} The input image with all bands sharpened to the spatial
 *  resolution of the panchromatic band.
 */
exports.sharpen = function (img, pan) {
  var panProj = pan.projection();
  // Store pan band name
  var panBand = pan.bandNames().get(0);
  img = img.resample("bilinear").reproject(panProj);

  var imgHsv = img.rgbToHsv();

  // Replace the value band with the pan band and convert back to RGB
  var imgRgb = imgHsv
    .addBands([pan])
    .select(["hue", "saturation", panBand])
    .hsvToRgb()
    .rename(img.bandNames());

  return imgRgb;
};
