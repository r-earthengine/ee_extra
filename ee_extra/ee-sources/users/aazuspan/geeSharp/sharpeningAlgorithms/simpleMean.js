/**
 * Sharpen an image using a simple mean, where each band is calculated as the
 * mean of the band and the panchromatic band.
 * @param {ee.Image} img An image to sharpen. All bands should spectrally
 *  overlap the panchromatic band to avoid spectral distortion.
 * @param {ee.Image} pan An single-band panchromatic image.
 * @return {ee.Image} The input image with all bands sharpened to the spatial
 *  resolution of the panchromatic band.
 */
exports.sharpen = function (img, pan) {
  var panProj = pan.projection();

  // Resample all bands to the panchromatic resolution
  var imgSharp = img.resample("bilinear").reproject(panProj);
  // Replace each band with the mean of that band and the pan band
  imgSharp = imgSharp.add(pan).multiply(0.5);

  return imgSharp;
};
