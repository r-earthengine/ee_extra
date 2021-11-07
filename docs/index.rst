eeExtra
=======

.. raw:: html

        <embed>
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
        </embed>
  
.. toctree::   
   :maxdepth: 2
   :caption: API Reference
   :hidden:      
   
   modules/index


**GitHub**: `https://github.com/r-earthengine/ee_extra <https://github.com/r-earthengine/ee_extra>`_

**Documentation**: `https://ee-extra.readthedocs.io <https://ee-extra.readthedocs.io>`_

**PyPI**: `https://pypi.python.org/pypi/ee_extra <https://pypi.python.org/pypi/ee_extra>`_

**Conda-forge**: `https://anaconda.org/conda-forge/ee_extra <https://anaconda.org/conda-forge/ee_extra>`_

Overview
--------

`Google Earth Engine <https://earthengine.google.com/>`_ (GEE) is a cloud-based service for 
geospatial processing of vector and raster data. The Earth Engine platform has a 
`JavaScript and a Python API <https://developers.google.com/earth-engine/guides>`_ with 
different methods to process geospatial objects. Google Earth Engine also provides a 
`HUGE PETABYTE-SCALE CATALOG <https://developers.google.com/earth-engine/datasets/>`_ of 
raster and vector data that users can process online. 

There are a lot of fantastic third-party GEE packages and projects around GitHub. However,
most of them are coded in JavaScript or Python, and they are not straightforward
to translate to R, Julia, or other programming languages. The main goal of `eeExtra` is
to guarantee a smooth `import` of these projects in other programming languages by
standardizing different methods and enabling the use of JavaScript modules outside the
`Code Editor <https://code.earthengine.google.com/>`_.

.. raw:: html

        <embed>
                <p align="center">
                <img src="https://user-images.githubusercontent.com/16768318/139555895-d384832a-28fb-4812-a836-4d4455faf443.png" alt="ee_extra_diagram" width="650">
                </p>
        </embed>

Some of the `eeExtra` features are listed here:

- Automatic scaling and offsetting.
- Spectral Indices computation (using `Awesome Spectral Indices <https://github.com/davemlz/awesome-spectral-indices>`_).
- Clouds and shadows masking.
- STAC related functions.

And the most important feature:

- Enabling the usage of JavaScript modules outside the Code Editor.


How does it work?
-----------------

`eeExtra` is a Python package, just like any other, but it is a *ninja* that serves as a 
methods provider for different environments: R, Julia and Python itself. `eeExtra` 
accomplish this by being the powerhouse of some amazing packages such as `rgee <https://github.com/r-spatial/rgee>`_,
`rgee+ <https://github.com/r-earthengine/rgeeExtra>`_, and `eemont <https://github.com/davemlz/eemont>`_.

Public JavaScript module can also be used outside the Code Editor in these packages
through `eeExtra`. For this, `eeExtra` implements a rigorous JavaScript translation
module that allows users to install, require and use JavaScript modules as if they
were on the Code Editor!

You may be wondering *"Why is it a ninja package?"*, well, that's a valid question,
the whole point of `eeExtra` resides in the fact that nobody has to use `eeExtra` itself,
but rather use one of the packages that are powered by `eeExtra`! :) 


Installation
------------

Install the latest version from PyPI:

.. code-block:: python

        pip install ee_extra


Install soft ee_extra dependencies:

.. code-block:: python

        pip install jsbeautifier regex

Upgrade `eeExtra` by running:

.. code-block:: python

        pip install -U ee_extra

Install the latest version from conda-forge:

.. code-block:: python

        conda install -c conda-forge ee_extra

Install the latest dev version from GitHub by running:

.. code-block:: python

        pip install git+https://github.com/r-earthengine/ee_extra