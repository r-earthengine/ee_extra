eeExtra
=======

A ninja Python package behind `rgee <https://github.com/r-spatial/rgee>`, `rgeeExtra <https://github.com/r-earthengine/rgeeExtra>` and `eemont <https://github.com/davemlz/eemont>`

.. image:: https://img.shields.io/pypi/v/ee_extra.svg
        :target: https://pypi.python.org/pypi/ee_extra
        
.. image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
        :target: https://opensource.org/licenses/Apache-2.0
        
.. image:: https://readthedocs.org/projects/ee-extra/badge/?version=latest
        :target: https://ee-extra.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://github.com/r-earthengine/ee_extra/actions/workflows/tests.yml/badge.svg
        :target: https://github.com/r-earthengine/ee_extra/actions/workflows/tests.yml

.. image:: https://github.com/r-earthengine/ee_extra/actions/workflows/update_awesome_spectral_indices.yml/badge.svg
        :target: https://github.com/r-earthengine/ee_extra/actions/workflows/update_awesome_spectral_indices.yml

.. image:: https://github.com/r-earthengine/ee_extra/actions/workflows/update_gee_stac_ids.yml/badge.svg
        :target: https://github.com/r-earthengine/ee_extra/actions/workflows/update_gee_stac_ids.yml

.. image:: https://github.com/r-earthengine/ee_extra/actions/workflows/update_gee_stac_scale_offset.yml/badge.svg
        :target: https://github.com/r-earthengine/ee_extra/actions/workflows/update_gee_stac_scale_offset.yml
        
.. image:: https://img.shields.io/badge/David-buy%20me%20a%20coffee-ff69b4.svg
        :target: https://www.buymeacoffee.com/davemlz
        
.. image:: https://img.shields.io/badge/Cesar-buy%20me%20a%20coffee-ff69b4.svg
        :target: https://www.buymeacoffee.com/csay
        
.. image:: https://static.pepy.tech/personalized-badge/ee_extra?period=total&units=international_system&left_color=grey&right_color=green&left_text=Downloads
        :target: https://pepy.tech/project/ee_extra
        
.. image:: https://img.shields.io/badge/GEE%20Community-Developer%20Resources-00b6ff.svg
        :target: https://developers.google.com/earth-engine/tutorials/community/developer-resources
        
.. image:: https://img.shields.io/twitter/follow/csaybar?style=social
        :target: https://twitter.com/csaybar        

.. image:: https://img.shields.io/twitter/follow/dmlmont?style=social
        :target: https://twitter.com/dmlmont
        
.. image:: https://joss.theoj.org/papers/34696c5b62c50898b4129cbbe8befb0a/status.svg
    :target: https://joss.theoj.org/papers/34696c5b62c50898b4129cbbe8befb0a
    
.. image:: https://joss.theoj.org/papers/10.21105/joss.02272/status.svg
    :target: https://doi.org/10.21105/joss.02272
        
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
  

- GitHub: `https://github.com/r-earthengine/ee_extra <https://github.com/r-earthengine/ee_extra>`_
- Documentation: `https://ee-extra.readthedocs.io/ <https://ee-extra.readthedocs.io/>`_
- PyPI: `https://pypi.org/project/ee-extra/ <https://pypi.org/project/ee-extra/>`_


**Table of Contents**

- `Overview`_
- `Google Earth Engine Community: Developer Resources`_
- `Powerhouse of...`_
- `Installation`_
- `License`_
- `How to cite`_
- `Artists`_
- `Credits`_


Overview
-------------------

`Google Earth Engine <https://earthengine.google.com/>`_ is a cloud-based service for geospatial processing of vector and raster data. The Earth Engine platform has a `JavaScript and a Python API <https://developers.google.com/earth-engine/guides>`_ with different methods to process geospatial objects. Google Earth Engine also provides a `HUGE PETABYTE-SCALE CATALOG <https://developers.google.com/earth-engine/datasets/>`_ of raster and vector data that users can process online (e.g. Landsat Missions Image Collections, Sentinel Missions Image Collections, MODIS Products Image Collections, World Database of Protected Areas, etc.). 

There are a lot of fantastic third-party GEE packages and projects around GitHub. However, most of them are coded in JavaScript or in a Python code style that is not straightforward to translate to R, Julia, or other programming languages. The main goal of **ee_extra** is to guarantee a smooth import of these projects. We re-wrote the most popular JavaScript and Python EE algorithms minimizing the dependencies to just two Python packages: **earthengine-api** and **NumPy**. Third-party GEE tools that can not meet this stipulation will not be added to **ee_extra**. Additionally, rigorous checking of code style (**black**) and documentation style (**darglint**) will be carried out to guarantee a smooth conversion of Python documentation into, for instance, R documentation (**rgee::ee_help**).

.. image:: https://user-images.githubusercontent.com/16768318/119165340-ad784f80-ba5d-11eb-8d00-699eac93fb2c.png
    :alt: ee_extra


Google Earth Engine Community: Developer Resources
-----------------------------------------------------

The ee_extra Python package can be found indirectly in the `Earth Engine Community: Developer Resources <https://developers.google.com/earth-engine/tutorials/community/developer-resources>`_ as the powerhouse of `eemont <https://github.com/davemlz/eemont>`_, `rgee <https://github.com/r-spatial/rgee>`_ and `rgeeExtra <https://github.com/r-earthengine/rgeeExtra>`_.


Powerhouse of...
--------------------

- `rgee <https://github.com/r-spatial/rgee>`
- `rgeeExtra <https://github.com/r-earthengine/rgeeExtra>`
- `eemont <https://github.com/davemlz/eemont>`


Installation
------------

Install the latest eemont version from PyPI by running:

.. code-block::   
      
   pip install ee_extra

Upgrade eemont by running:

.. code-block::   
      
   pip install -U ee_extra

Install the development version from GitHub by running:

.. code-block::   
      
   pip install git+https://github.com/r-earthengine/ee_extra
   
Install the latest eemont version from conda-forge by running (SOON):

.. code-block::   
      
   conda install -c conda-forge ee_extra


License
-------

The project is licensed under the Apache v.2.0 license.


How to cite
-----------

Do you like using ee_extra and think it is useful? Share the love by citing it through eemont and rgee!::

   Montero, D., (2021). eemont: A Python package that extends Google Earth Engine. Journal of Open Source Software, 6(62), 3168, https://doi.org/10.21105/joss.03168
   Aybar et al., (2020). rgee: An R package for interacting with Google Earth Engine. Journal of Open Source Software, 5(51), 2272, https://doi.org/10.21105/joss.02272
   
If required, here is the BibTex for both papers!::

   @article{Montero2021,
     doi = {10.21105/joss.03168},
     url = {https://doi.org/10.21105/joss.03168},
     year = {2021},
     publisher = {The Open Journal},
     volume = {6},
     number = {62},
     pages = {3168},
     author = {David Montero},
     title = {eemont: A Python package that extends Google Earth Engine},
     journal = {Journal of Open Source Software}
   }

   @Article{Aybar2020,
      doi = {10.21105/joss.02272},
      url = {https://doi.org/10.21105/joss.02272},
      publisher = {The Open Journal},
      title = {rgee: An R package for interacting with Google Earth Engine},
      author = {Cesar Aybar and Quisheng Wu and Lesly Bautista and Roy Yali and Antony Barja},
      journal = {Journal of Open Source Software},
      year = {2020},
    }


Artists
-------

- `César Aybar <https://github.com/csaybar>`_: Lead Developer.
- `David Montero Loaiza <https://github.com/davemlz>`_: Lead Developer.


Credits
-------

Special thanks to `Justin Braaten <https://github.com/jdbcode>`_ for reviewing the ee_extra proposal!