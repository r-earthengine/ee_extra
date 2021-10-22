<p align="center">
  <a href="https://github.com/r-earthengine/ee_extra"><img src="https://raw.githubusercontent.com/r-earthengine/ee_extra/master/docs/_static/logo_name.png" alt="spyndex"></a>
</p>
<p align="center">
    <em>A ninja python package that unifies the Google Earth Engine ecosystem:</em>
</p>
<p align="center">
    <b><a href="https://github.com/r-spatial/rgee" target="_blank">
    rgee</a> | <a href="https://github.com/r-earthengine/rgeeExtra" target="_blank">
    rgee+</a> | <a href="https://github.com/davemlz/eemont" target="_blank">
    eemont</a> </b>
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
    <img src="https://github.com/r-earthengine/ee_extra/actions/workflows/update_gee_stac_ids.yml/badge.svg" alt="License">
</a>
<a href="https://github.com/r-earthengine/ee_extra/actions/workflows/update_gee_stac_scale_offset.yml" target="_blank">
    <img src="https://github.com/r-earthengine/ee_extra/actions/workflows/update_gee_stac_scale_offset.yml/badge.svg" alt="GitHub Sponsors">
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

You may be wondering *"Why is it a ninja python package?"*, well, that's a valid question,
the whole point of `eeExtra` resides in the fact that nobody has to use `eeExtra` itself,
but rather use one of the packages that are powered by `eeExtra`! :) 


## Installation

Install the latest version from PyPI:

```
pip install ee_extra
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
S2$scaleAndOffset()
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
S2 <- S2$scaleAndOffset()
S2$spectralIndices("EVI")
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
S2$getSTAC()
```
</td>
</tr>

</table>

### JavaScript Modules

This is perhaps the most important feature in `eeExtra`! What if you could use a
JavaScript module (originally just useful for the Code Editor) in python or R? Well,
wait no more for it!

<table>

<tr>
<th> JS (Code Editor) </th>
<th> Python (eemont) </th>
<th> R (rgee+) </th>
</tr>

<tr>
<td>
  
``` javascript
var usr = 'users/sofiaermida/'
var rep = 'landsat_smw_lst:'
var fld = 'modules/'
var fle = 'Landsat_LST.js'
var pth = usr+rep+fld+fle
var mod = require(pth)
var LST = mod.collection(
    ee.Geometry.Rectangle([
        -8.91,
        40.0,
        -8.3,
        40.4
    ]),
    'L8',
    '2018-05-15',
    '2018-05-31',
    true
)
```

</td>
<td>
  
``` python
import ee, eemont
ee.Initialize()
usr = 'users/sofiaermida/'
rep = 'landsat_smw_lst:'
fld = 'modules/'
fle = 'Landsat_LST.js'
pth = usr+rep+fld+fle
ee.install(pth)
mod = ee.require(pth)
LST = mod.collection(
    ee.Geometry.Rectangle([
        -8.91,
        40.0,
        -8.3,
        40.4
    ]),
    'L8',
    '2018-05-15',
    '2018-05-31',
    True
)
```

</td>
<td>

``` r
library(rgee)
library(rgeeExtra)
ee_Initialize()
usr <- 'users/sofiaermida/'
rep <- 'landsat_smw_lst:'
fld <- 'modules/'
fle <- 'Landsat_LST.js'
pth <- paste0(usr,rep,fld,fle)
mod <- ee$require(pth)
LST = mod$collection(
    ee$Geometry$Rectangle(c(
        -8.91,
        40.0,
        -8.3,
        40.4
    )),
    'L8',
    '2018-05-15',
    '2018-05-31',
    TRUE
)
```
</td>
</tr>

</table>