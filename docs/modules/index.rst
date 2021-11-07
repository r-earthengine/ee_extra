API Reference
=============

Welcome to the eeExtra API Reference!

.. toctree::   
   :maxdepth: 4   
   :caption: API Reference
   :hidden:      
   
   Image
   ImageCollection
   JavaScript
   QA
   Spectral
   STAC
   TimeSeries
   
Extra.Image
-----------

.. currentmodule:: ee_extra.Image.basic

.. autosummary::

   minvalue   
   maxvalue

Extra.ImageCollection
---------------------

.. currentmodule:: ee_extra.ImageCollection.core

.. autosummary::

   closest

Extra.JavaScript
----------------

.. currentmodule:: ee_extra.JavaScript.install

.. autosummary::

   install
   uninstall

.. currentmodule:: ee_extra.JavaScript.main

.. autosummary::

   ee_js_to_py
   ee_require
   ee_translate

Extra.QA
--------

.. currentmodule:: ee_extra.QA.clouds

.. autosummary::

   maskClouds

.. currentmodule:: ee_extra.QA.pipelines

.. autosummary::

   preprocess

Extra.Spectral
--------------

.. currentmodule:: ee_extra.Spectral.core

.. autosummary::

   indices
   listIndices
   spectralIndices
   tasseledCap

Extra.STAC
----------

.. currentmodule:: ee_extra.STAC.core

.. autosummary::

   getCitation
   getDOI
   getOffsetParams   
   getScaleParams
   getSTAC
   listDatasets
   scaleAndOffset

Extra.TimeSeries
----------------

.. currentmodule:: ee_extra.TimeSeries.core

.. autosummary::

   getTimeSeriesByRegion
   getTimeSeriesByRegions