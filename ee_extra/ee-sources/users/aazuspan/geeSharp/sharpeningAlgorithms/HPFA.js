var utils = require("users/aazuspan/geeSharp:utils.js");

/**
 * Sharpen an image using an additive high-pass filter, where spatial detail is
 * extracted from a panchromatic band using a high-pass filter and added into
 * the multispectral bands.
 * @param {ee.Image} img An image to sharpen. All bands should spectrally
 *  overlap the panchromatic band to avoid spectral distortion.
 * @param {ee.Image} pan An single-band panchromatic image.
 * @param {number} kernelWidth The width of the high-pass filter kernel. This
 *  defaults to 2 * (msRes / panRes) + 1, where msRes is the multispectral
 *  pixel width and panRes is the panchromatic pixel width. For example,
 *  Landsat 8 has msRes of 30 and panRes of 15, so (2 * (30 / 15) + 1) = 5.
 * @return {ee.Image} The input image with all bands sharpened to the spatial
 *  resolution of the panchromatic band.
 */
exports.sharpen = function (img, pan, kernelWidth) {
  // Calculate default kernel width following Gangofner et al 2008
  if (utils.isMissing(kernelWidth)) {
    var panRes = pan.projection().nominalScale();
    var msRes = img.projection().nominalScale();

    kernelWidth = ee.Number(msRes.divide(panRes).multiply(2).add(1));
  } else {
    // Make sure it's an ee.Number so it has the necessary methods
    kernelWidth = ee.Number(kernelWidth);
  }

  // Resample multispectral bands to the panchromatic resolution
  img = img.resample("bilinear");
  img = img.reproject(pan.projection());

  pan = pan.resample("bilinear");

  // Calculate kernel center value following Gangofner et al 2008
  var centerVal = kernelWidth.pow(2).subtract(1);
  // Get the index of the kernel center
  var center = kernelWidth.divide(2).int();
  // Build a single kernel row
  var kernelRow = ee.List.repeat(-1, kernelWidth);
  // Build a kernel out of rows
  var kernel = ee.List.repeat(kernelRow, kernelWidth);
  // Replace the center position of the kernel with the center value
  kernel = kernel.set(
    center,
    ee.List(kernel.get(center)).set(center, centerVal)
  );
  // Use a normalized kernel to minimize spectral distortion
  kernel = ee.Kernel.fixed({ weights: kernel, normalize: true });

  // Use a high pass filter to extract spatial detail from the pan band
  var panHPF = pan.convolve(kernel);
  // Add pan HPF to each multispectral band
  var imgHPFA = img.add(panHPF);

  return imgHPFA;
};
