/**
 * Convert an n-band image into an image collection with n images
 * @param {ee.Image} img A multiband image.
 * @return {ee.ImageCollection} A collection where each image is a band of the
 *  input image.
 */
exports.multibandToCollection = function (img) {
   return ee.ImageCollection(
     img.bandNames().map(function (name) {
       return img.select([name]);
     })
   );
};

/**
 * Create a constant image where each band represents the reduced value of the
 * corresponding band of the input image.
 * @param {ee.Image} img The input image to calculate reduced values for.
 * @param {ee.Reducer} reducer The reducer to apply to the image, such as
 *  ee.Reducer.min()
 * @param {ee.Geometry} geometry The region to generate image statistics over.
 *  Defaults to the geometry of the input image.
 * @param {ee.Number} scale The scale to generate image statistics at. Defaults
 *  to the nominal scale of the input image.
 * @param {ee.Number} maxPixels Maximum number of pixels used to calculate
 *  statistics.
 * @return {ee.Image} An image with the same number of bands as the input
 *  image, where each band is a constant value of the reduced value of the
 *  corresponding band of the input image.
 */
exports.reduceImage = function (img, reducer, geometry, scale, maxPixels) {
  if (exports.isMissing(geometry)) {
    geometry = img.geometry();
  }

  if (exports.isMissing(scale)) {
    scale = img.projection().nominalScale();
  }

  if (exports.isMissing(maxPixels)) {
    maxPixels = 1e12;
  }

  // Calculate the reduced image value(s)
  var imgReducedVal = img.reduceRegion({
    reducer: reducer,
    geometry: geometry,
    scale: scale,
    maxPixels: maxPixels,
  });

  var imgReduced = imgReducedVal.toImage(img.bandNames());
  return imgReduced;
};

/**
 * Create a constant image where each band represents the range value of the
 * corresponding band of the input image.
 * @param {ee.Image} img The input image to calculate range values for.
 * @param {ee.Geometry} geometry The region to generate image statistics over.
 * @param {ee.Number} scale The scale to generate image statistics at.
 * @param {ee.Number} maxPixels Maximum number of pixels used to calculate
 *  statistics.
 * @return {ee.Image} An image with the same number of bands as the input
 *  image, where each band is a constant value of the range value of the
 *  corresponding band of the input image.
 */
exports.getImageRange = function (img, geometry, scale, maxPixels) {
  var imgMax = exports.reduceImage(
    img,
    ee.Reducer.max(),
    geometry,
    scale,
    maxPixels
  );
  var imgMin = exports.reduceImage(
    img,
    ee.Reducer.min(),
    geometry,
    scale,
    maxPixels
  );
  var imgRange = imgMax.subtract(imgMin);
  return imgRange;
};

/**
 * Rescale the mean and standard deviation of a target image to match a
 * reference image.
 * @param {ee.Image} targetImage An image to rescale.
 * @param {ee.Image} referenceImage An image to rescale towards.
 * @param {ee.Geometry} geometry The region to generate image statistics over.
 * @param {ee.Number} scale The scale to generate image statistics at.
 * @param {ee.Number} maxPixels Maximum number of pixels used to calculate
 *  statistics.
 * @return {ee.Image} A rescaled version of targetImage.
 */
exports.linearHistogramMatch = function (
  targetImage,
  referenceImage,
  geometry,
  scale,
  maxPixels
) {
  var offsetTarget = exports.reduceImage(
    targetImage,
    ee.Reducer.mean(),
    geometry,
    scale,
    maxPixels
  );
  var offset = exports.reduceImage(
    referenceImage,
    ee.Reducer.mean(),
    geometry,
    scale,
    maxPixels
  );
  var rescale = exports
    .reduceImage(
      referenceImage,
      ee.Reducer.stdDev(),
      geometry,
      scale,
      maxPixels
    )
    .divide(
      exports.reduceImage(
        targetImage,
        ee.Reducer.stdDev(),
        geometry,
        scale,
        maxPixels
      )
    );

  var rescaledTarget = targetImage
    .subtract(offsetTarget)
    .multiply(rescale)
    .add(offset);
  return rescaledTarget;
};

/**
 * Check if an object has a value. Helpful for finding missing arguments.
 * @param {object} x Any object
 * @return {boolean} True if the object is missing, false if it is not.
 */
exports.isMissing = function (x) {
  if (x === undefined || x === null) {
    return true;
  }
  return false;
};

/**
 * Calculate an intensity band from the bands of an image using fixed band weights.
 * @param {ee.Image} img An image to calculate intensity from.
 * @param {ee.List} weights A list of weights for each band. Length must equal the
 *  number of bands in img.
 * @return {ee.Image} A single band image representing the weighted intensity of
 *  the original image.
 */
exports.calculateWeightedIntensity = function (img, weights) {
  // Convert the weights to a multiband constant image. This will allow weights
  // to work whether it is an array or an ee.List
  var weigthImg = ee.Image.constant(weights);

  var weightedImg = img.multiply(weigthImg);

  var intensity = weightedImg.reduce(ee.Reducer.sum());

  return intensity;
};