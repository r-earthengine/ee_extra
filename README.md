
<p align="center">
  <img src="https://user-images.githubusercontent.com/16768318/139555722-cc8cd77e-aa51-455e-bed3-0cac76b59258.png" alt="ee_extra" width="800"></a>
</p>
<p align="center">
    <em>A Python package that unifies the Google Earth Engine ecosystem.</em>
</p>
<p align="center">
  <b>
    <a href="https://github.com/KMarkert/EarthEngine.jl" target="_blank">EarthEngine.jl</a> |
    <a href="https://github.com/r-spatial/rgee" target="_blank"> rgee </a> | 
    <a href="https://github.com/r-earthengine/rgeeExtra" target="_blank"> rgee+ </a> | 
    <a href="https://github.com/davemlz/eemont" target="_blank"> eemont</a>
  </b>
</p>
<p align="center">
<a href='https://pypi.python.org/pypi/ee_extra'>
    <img src='https://img.shields.io/pypi/v/ee_extra.svg' alt='PyPI' />
</a>
<a href='https://anaconda.org/conda-forge/ee_extra'>
    <img src='https://img.shields.io/conda/vn/conda-forge/ee_extra.svg' alt='conda-forge' />
</a>
<a href="https://opensource.org/licenses/Apache-2.0" target="_blank">
    <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License">
</a>
<a href='https://ee-extra.readthedocs.io/en/latest/?badge=latest'>
    <img src='https://readthedocs.org/projects/ee-extra/badge/?version=latest' alt='Documentation Status' />
</a>
<a href="https://github.com/r-earthengine/ee_extra/actions/workflows/tests.yml" target="_blank">
    <img src="https://github.com/r-earthengine/ee_extra/actions/workflows/tests.yml/badge.svg" alt="Tests">
</a>
<a href="https://github.com/r-earthengine/ee_extra/actions/workflows/update_awesome_spectral_indices.yml" target="_blank">
    <img src="https://github.com/r-earthengine/ee_extra/actions/workflows/update_awesome_spectral_indices.yml/badge.svg" alt="Awesome Spectral Indices">
</a>
<a href="https://github.com/r-earthengine/ee_extra/actions/workflows/update_gee_stac_ids.yml" target="_blank">
    <img src="https://github.com/r-earthengine/ee_extra/actions/workflows/update_gee_stac_ids.yml/badge.svg" alt="GEE STAC">
</a>
<a href="https://github.com/r-earthengine/ee_extra/actions/workflows/update_gee_stac_scale_offset.yml" target="_blank">
    <img src="https://github.com/r-earthengine/ee_extra/actions/workflows/update_gee_stac_scale_offset.yml/badge.svg" alt="Scale and Offset">
</a>
<a href="https://github.com/r-earthengine/ee_extra/actions/workflows/update_ee_appshot.yml" target="_blank">
    <img src="https://github.com/r-earthengine/ee_extra/actions/workflows/update_ee_appshot.yml/badge.svg" alt="ee-appshot">
</a>
<a href="https://github.com/psf/black" target="_blank">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Black">
</a>
<a href="https://pycqa.github.io/isort/" target="_blank">
    <img src="https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336" alt="isort">
</a>
</p>

---

**GitHub**: [https://github.com/r-earthengine/ee_extra](https://github.com/r-earthengine/ee_extra)

**Documentation**: [https://ee-extra.readthedocs.io](https://ee-extra.readthedocs.io)

**PyPI**: [https://pypi.python.org/pypi/ee_extra](https://pypi.python.org/pypi/ee_extra)

**Conda-forge**: [https://anaconda.org/conda-forge/ee_extra](https://anaconda.org/conda-forge/ee_extra)

---

## Overview

[Google Earth Engine](https://earthengine.google.com/) (GEE) is a cloud-based service for 
geospatial processing of vector and raster data. The Earth Engine platform has a 
[JavaScript and a Python API](https://developers.google.com/earth-engine/guides) with 
different methods to process geospatial objects. Google Earth Engine also provides a 
[HUGE PETABYTE-SCALE CATALOG](https://developers.google.com/earth-engine/datasets/) of 
raster and vector data that users can process online. 

There are a lot of fantastic third-party GEE packages and projects around GitHub. However,
most of them are coded in JavaScript or Python, and they are not straightforward
to translate to R, Julia, or other programming languages. The main goal of `eeExtra` is
to guarantee a smooth `import` of these projects in other programming languages by
standardizing different methods and enabling the use of JavaScript modules outside the
[Code Editor](https://code.earthengine.google.com/).


<p align="center">
  <img src="https://user-images.githubusercontent.com/16768318/139555895-d384832a-28fb-4812-a836-4d4455faf443.png" alt="ee_extra_diagram" width="650">
</p>

Some of the `eeExtra` features are listed here:

- Automatic scaling and offsetting.
- Spectral Indices computation (using [Awesome Spectral Indices](https://github.com/davemlz/awesome-spectral-indices)).
- Clouds and shadows masking.
- STAC related functions.

And the most important feature:

- Enabling the usage of JavaScript modules outside the Code Editor.


## How does it work?

`eeExtra` is a Python package, just like any other, but it is a *ninja* that serves as a 
methods provider for different environments: R, Julia and Python itself. `eeExtra` 
accomplish this by being the powerhouse of some amazing packages such as [rgee](https://github.com/r-spatial/rgee),
[rgee+](https://github.com/r-earthengine/rgeeExtra), and [eemont](https://github.com/davemlz/eemont).

Public JavaScript module can also be used outside the Code Editor in these packages
through `eeExtra`. For this, `eeExtra` implements a rigorous JavaScript translation
module that allows users to install, require and use JavaScript modules as if they
were on the Code Editor!

You may be wondering *"Why is it a ninja package?"*, well, that's a valid question,
the whole point of `eeExtra` resides in the fact that nobody has to use `eeExtra` itself,
but rather use one of the packages that are powered by `eeExtra`! :) 


## Installation

Install the latest version from PyPI:

```
pip install ee_extra
```

Install soft ee_extra dependencies:

```
pip install jsbeautifier regex
```

Upgrade `eeExtra` by running:

```
pip install -U ee_extra
```

Install the latest version from conda-forge:

```
conda install -c conda-forge ee_extra
```

Install the latest dev version from GitHub by running:

```
pip install git+https://github.com/r-earthengine/ee_extra
```

## Features

Let's see some of the awesome features of `eeExtra` and how to use them from the powered
packages in python and R!

### Scale and Offset

Most datasets in the data catalog are scaled and in order to get their real values,
we have to scale (and sometimes offset) them!

<table>

<tr>
<th> Python (eemont) </th>
<th> R (rgee+) </th>
<th> Julia (EarthEngine.jl) </th>
</tr>

<tr>
<td>
  
``` python
import ee, eemont
ee.Initialize()
db = 'COPERNICUS/S2_SR'
S2 = ee.ImageCollection(db)
S2.scaleAndOffset()
```

</td>
<td>

``` r
library(rgee)
library(rgeeExtra)
ee_Initialize()
db <- 'COPERNICUS/S2_SR'
S2 <- ee$ImageCollection(db)
ee_extra_scaleAndOffset(S2)
```
</td>

<td>

``` julia
using PyCall
using EarthEngine

Initialize()

ee_extra = pyimport("ee_extra")
ee_core = ee_extra.STAC.core
db = "COPERNICUS/S2_SR"
S2 = ee.ImageCollection(db)
ee_core.scaleAndOffset(S2)
```
</td>


</tr>

</table>

### Spectral Indices

Do you know the [Awesome Spectral Indices](https://github.com/davemlz/awesome-spectral-indices)? 
Well, you can compute them automatically with `eeExtra`! 

<table>

<tr>
<th> Python (eemont) </th>
<th> R (rgee+) </th>
<th> Julia (EarthEngine.jl) </th>
</tr>

<tr>
<td>
  
``` python
import ee, eemont
ee.Initialize()
db = 'COPERNICUS/S2_SR'
S2 = ee.ImageCollection(db)
S2 = S2.scaleAndOffset()
S2.spectralIndices("EVI")
```

</td>
<td>

``` r
library(rgee)
library(rgeeExtra)
ee_Initialize()
db <- 'COPERNICUS/S2_SR'
S2 <- ee$ImageCollection(db)
S2 <- ee_extra_scaleAndOffset(S2)
ee_extra_spIndices(S2, "EVI")
```
</td>

<td>
  
```julia
using PyCall
using EarthEngine

Initialize()

ee_extra = pyimport("ee_extra")
ee_core = ee_extra.STAC.core
ee_sp = ee_extra.Spectral.core
db = "COPERNICUS/S2_SR"
S2 = ee.ImageCollection(db)
S2 = ee_core.scaleAndOffset(S2)
ee_sp.spectralIndices(S2, "EVI")
```
  
</td>  
</tr>
</table>

### STAC features

Access STAC properties easily!

<table>

<tr>
<th> Python (eemont) </th>
<th> R (rgee+) </th>
<th> Julia (EarthEngine.jl) </th>
</tr>

<tr>
<td>
  
``` python
import ee, eemont
ee.Initialize()
db = 'COPERNICUS/S2_SR'
S2 = ee.ImageCollection(db)
S2.getSTAC()
```

</td>
<td>

``` r
library(rgee)
library(rgeeExtra)
ee_Initialize()
db <- 'COPERNICUS/S2_SR'
S2 <- ee$ImageCollection(db)
ee_extra_getSTAC()
```
</td>
  

<td>

``` julia
  
using PyCall
using EarthEngine

Initialize()

ee_extra = pyimport("ee_extra")
ee_core = ee_extra.STAC.core
db = "COPERNICUS/S2_SR"
S2 = ee.ImageCollection(db)
ee_core.getSTAC(S2)

```
</td>
  
</tr>

</table>

### JavaScript Modules

This is perhaps the most important feature in `eeExtra`! What if you could use a
JavaScript module (originally just useful for the Code Editor) in python or R? Well,
wait no more for it!

  - **JS Code Editor**

``` javascript
var mod = require('users/sofiaermida/landsat_smw_lst:modules/Landsat_LST.js')

var geom = ee.Geometry.Rectangle(-8.91, 40.0, -8.3, 40.4)
var LST = mod.collection("L8", "2018-05-15", "2018-05-31", geom, true)

print(LST)
```

  - **Python eemont**  

``` python
import ee, eemont

ee.Initialize()
module = 'users/sofiaermida/landsat_smw_lst:modules/Landsat_LST.js'
ee.install(module)
mod = ee.require(module)

geom = ee.Geometry.Rectangle(-8.91, 40.0, -8.3, 40.4)
LST = mod.collection("L8", "2018-05-15", "2018-05-31", geom, True)
print(LST)
```

  - **R rgeeExtra**  

``` r
library(rgee)
library(rgeeExtra)

ee_Initialize()

lsmod <- 'users/sofiaermida/landsat_smw_lst:modules/Landsat_LST.js'
mod <- module(lsmod)

geom <- ee$Geometry$Rectangle(-8.91, 40.0, -8.3, 40.4)
LST <- mod$collection("L8", "2018-05-15", "2018-05-31", geom, TRUE)
print(LST)
```
  
  - **Julia EarthEngine.jl**

``` julia
using PyCall
using EarthEngine

Initialize()

ee_extra = pyimport("ee_extra")
landsat_module = "users/sofiaermida/landsat_smw_lst:modules/Landsat_LST.js"
ee_extra.install(landsat_module)
lsmodule = ee_extra.require(landsat_module)

geom = Rectangle(-8.91, 40.0, -8.3, 40.4)
LST = lsmodule.collection("L8", "2018-05-15", "2018-05-31", geom, true)
print(LST)
```
