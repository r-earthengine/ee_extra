/*
Copyright (c) 2018 Gennadii Donchyts. All rights reserved.

This work is licensed under the terms of the MIT license.  
For a copy, see <https://opensource.org/licenses/MIT>.
*/

/***
 * Detect cloud shadow by projection cloud (casting) using sun elevation/azimuth.
 * Example: https://code.earthengine.google.com/702e270c6f8a4d09cea2a027a49d3e2f
 *
 * θ - zenith, degrees
 * φ - azimuth, degrees
 */
function projectCloudShadow(cloudMask, cloudHeight, φ, θ) {
    cloudHeight = ee.Number(cloudHeight);

    // convert to radians
    var π = Math.PI;
    θ = ee.Number(0.5).multiply(π).subtract(ee.Number(θ).multiply(π).divide(180.0));
    φ = ee.Number(φ).multiply(π).divide(180.0).add(ee.Number(0.5).multiply(π));

    // compute shadow offset (vector length)
    var offset = θ.tan().multiply(cloudHeight);

    // compute x, y components of the vector
    var proj = cloudMask.projection();
    var nominalScale = proj.nominalScale();
    var x = φ.cos().multiply(offset).divide(nominalScale).round();
    var y = φ.sin().multiply(offset).divide(nominalScale).round();

    return cloudMask.changeProj(proj, proj.translate(x, y)).set('height', cloudHeight)
}

/*** 
 * Casts cloud mask given a number of cloud heights and sun parameters.
 */
function castCloudShadows(cloudMask, cloudHeights, sunAzimuth, sunZenith) {
  return cloudHeights.map(function (cloudHeight) {
      return projectCloudShadow(cloudMask, cloudHeight, sunAzimuth, sunZenith);
  });
}

/***
 * Estimates cloud shadow mask from image sun parameters.
 */
function computeCloudShadowMask(sunElevation, sunAzimuth, cloudMask, options) {
  var maxCloudHeight = 8000 // in image pixel units
  var cloudHeightStep = 200
  var radiusDilate = 10
  var radiusErode = 3
  
  if(options) {
    maxCloudHeight = options.maxCloudHeight || maxCloudHeight
    cloudHeightStep = options.cloudHeightStep || cloudHeightStep
    radiusDilate = options.radiusDilate || radiusDilate
    radiusErode = options.radiusErode || radiusErode
  }
  
  // generate cloud heights
  var cloudHeights = ee.List.sequence(100, maxCloudHeight, cloudHeightStep);
  
  // cast cloud shadows
  var cloudShadowMask = ee.ImageCollection(castCloudShadows(cloudMask, cloudHeights, sunAzimuth, sunElevation)).max();
  
  // remove clouds
  cloudShadowMask = cloudShadowMask.updateMask(cloudMask.not());

  return cloudShadowMask;
}
