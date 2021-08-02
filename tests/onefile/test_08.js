/*
Copyright (c) 2018 Gennadii Donchyts. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.
*/

/***
 * The script computes surface water mask using Canny Edge detector and Otsu thresholding
 * See the following paper for details: http://www.mdpi.com/2072-4292/8/5/386
 *
 * Author: Gennadii Donchyts (gennadiy.donchyts@gmail.com)
 * Contributors: Nicholas Clinton (nclinton@google.com) - re-implemented otsu() using ee.Array
 *
 * Usage:
 *
 * var thresholding = require('users/gena/packages:thresholding')
 *
 * var th = thresholding.computeThresholdUsingOtsu(image, scale, bounds, cannyThreshold, cannySigma, minValue, ...)
 *
 */

 /***
 * Return the DN that maximizes interclass variance in B5 (in the region).
 */
var otsu = function(histogram) {
    histogram = ee.Dictionary(histogram);

    var counts = ee.Array(histogram.get('histogram'));
    var means = ee.Array(histogram.get('bucketMeans'));
    var size = means.length().get([0]);
    var total = counts.reduce(ee.Reducer.sum(), [0]).get([0]);
    var sum = means.multiply(counts).reduce(ee.Reducer.sum(), [0]).get([0]);
    var mean = sum.divide(total);

    var indices = ee.List.sequence(1, size);

    // Compute between sum of squares, where each mean partitions the data.
    var bss = indices.map(function(i) {
        var aCounts = counts.slice(0, 0, i);
        var aCount = aCounts.reduce(ee.Reducer.sum(), [0]).get([0]);
        var aMeans = means.slice(0, 0, i);
        var aMean = aMeans.multiply(aCounts)
            .reduce(ee.Reducer.sum(), [0]).get([0])
            .divide(aCount);
        var bCount = total.subtract(aCount);
        var bMean = sum.subtract(aCount.multiply(aMean)).divide(bCount);
        return aCount.multiply(aMean.subtract(mean).pow(2)).add(
            bCount.multiply(bMean.subtract(mean).pow(2)));
    });

    // Return the mean value corresponding to the maximum BSS.
    return means.sort(bss).get([-1]);
};


/***
 * Compute a threshold using Otsu method (bimodal)
 */
function computeThresholdUsingOtsu(image, scale, bounds, cannyThreshold, cannySigma, minValue, debug, minEdgeLength, minEdgeGradient, minEdgeValue) {
    // clip image edges
    var mask = image.mask().gt(0).clip(bounds).focal_min(ee.Number(scale).multiply(3), 'circle', 'meters');

    // detect sharp changes
    var edge = ee.Algorithms.CannyEdgeDetector(image, cannyThreshold, cannySigma);
    edge = edge.multiply(mask);

    if(minEdgeLength) {
        var connected = edge.mask(edge).lt(cannyThreshold).connectedPixelCount(200, true);

        var edgeLong = connected.gte(minEdgeLength);

        if(debug) {
          print('Edge length: ', ui.Chart.image.histogram(connected, bounds, scale, buckets))

          Map.addLayer(edge.mask(edge), {palette:['ff0000']}, 'edges (short)', false);
        }

        edge = edgeLong;
    }

    // buffer around NDWI edges
    var edgeBuffer = edge.focal_max(ee.Number(scale), 'square', 'meters');

    if(minEdgeValue) {
      var edgeMin = image.reduceNeighborhood(ee.Reducer.min(), ee.Kernel.circle(ee.Number(scale), 'meters'))

      edgeBuffer = edgeBuffer.updateMask(edgeMin.gt(minEdgeValue))

      if(debug) {
        Map.addLayer(edge.updateMask(edgeBuffer), {palette:['ff0000']}, 'edge min', false);
      }
    }

    if(minEdgeGradient) {
      var edgeGradient = image.gradient().abs().reduce(ee.Reducer.max()).updateMask(edgeBuffer.mask())

      var edgeGradientTh = ee.Number(edgeGradient.reduceRegion(ee.Reducer.percentile([minEdgeGradient]), bounds, scale).values().get(0))

      if(debug) {
        print('Edge gradient threshold: ', edgeGradientTh)

        Map.addLayer(edgeGradient.mask(edgeGradient), {palette:['ff0000']}, 'edge gradient', false);

        print('Edge gradient: ', ui.Chart.image.histogram(edgeGradient, bounds, scale, buckets))
      }

      edgeBuffer = edgeBuffer.updateMask(edgeGradient.gt(edgeGradientTh))
    }

    edge = edge.updateMask(edgeBuffer)
    var edgeBuffer = edge.focal_max(ee.Number(scale).multiply(1), 'square', 'meters');
    var imageEdge = image.mask(edgeBuffer);

    if(debug) {
      Map.addLayer(imageEdge, {palette:['222200', 'ffff00']}, 'image edge buffer', false)
    }

    // compute threshold using Otsu thresholding
    var buckets = 100;
    var hist = ee.Dictionary(ee.Dictionary(imageEdge.reduceRegion(ee.Reducer.histogram(buckets), bounds, scale)).values().get(0));

    var threshold = ee.Algorithms.If(hist.contains('bucketMeans'), otsu(hist), minValue);
    threshold = ee.Number(threshold)


    if(debug) {
        // experimental
        // var jrc = ee.Image('JRC/GSW1_0/GlobalSurfaceWater').select('occurrence')
        // var jrcTh = ee.Number(ee.Dictionary(jrc.updateMask(edge).reduceRegion(ee.Reducer.mode(), bounds, scale)).values().get(0))
        // var water = jrc.gt(jrcTh)
        // Map.addLayer(jrc, {palette: ['000000', 'ffff00']}, 'JRC')
        // print('JRC occurrence (edge)', ui.Chart.image.histogram(jrc.updateMask(edge), bounds, scale, buckets))

        Map.addLayer(edge.mask(edge), {palette:['ff0000']}, 'edges', true);

        print('Threshold: ', threshold);

        print('Image values:', ui.Chart.image.histogram(image, bounds, scale, buckets));
        print('Image values (edge): ', ui.Chart.image.histogram(imageEdge, bounds, scale, buckets));
        Map.addLayer(mask.mask(mask), {palette:['000000']}, 'image mask', false);
    }

    return minValue !== 'undefined' ? threshold.max(minValue) : threshold;
}

exports.otsu = otsu
exports.computeThresholdUsingOtsu = computeThresholdUsingOtsu
