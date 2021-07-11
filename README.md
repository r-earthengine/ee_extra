# ee_extra

[![Python Version](https://img.shields.io/pypi/pyversions/ee_extra.svg)](https://pypi.org/project/ee_extra/)
[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/r-earthengine/ee_extra/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/github/license/r-earthengine/ee_extra)](https://github.com/r-earthengine/ee_extra/blob/master/LICENSE)
[![Documentation Status](https://readthedocs.org/projects/ee-extra/badge/?version=latest)](https://ee-extra.readthedocs.io/en/latest/?badge=latest)

**A ninja Python package behind rgee, rgeeExtra and eemont.** 


## Installation

Install the latest ee_extra version from PyPI by running:

```
pip install ee_extra
```

Upgrade ee_extra by running:

```
pip install -U ee_extra
```

Install the development version from GitHub by running:

```
pip install git+https://github.com/r-earthengine/ee_extra
```

Install the latest ee_extra version from conda-forge by running:

```
conda install -c conda-forge ee_extra
```

## Why do we need another GEE package?

There is a lot of fantastic third-party GEE packages and projects around GitHub. However, most of them are coded in JavaScript or in a Python code style that is not straightforward to translate to R, Julia, or other programming languages. The main goal of **ee_extra** is to guarantee a smooth import of these projects. We
re-write the most popular JavaScript and Python EE algorithms minimizing the dependencies to just two Python packages: **earthengine-api** and **NumPy**. Third-party GEE tools that can not meet this stipulation will not be added to ee_extra. Additionally, rigorous checking of code style (**black**) and documentation style (**darglint**) will be carried out to guarantee a smooth conversion of Python documentation into, for instance, R documentation (**rgee::ee_help**).

<h1 align="center">
<img src=https://user-images.githubusercontent.com/16768318/119165340-ad784f80-ba5d-11eb-8d00-699eac93fb2c.png width=60%>
</h1>


## License

The project is licensed under the Apache v.2.0 license.

## Contributing

Contributions to eemont are welcome! Here you will find how to do it:

- **Bugs**: If you find a bug, please report it by opening an issue. if possible, please attach the error, code, version, and other details.
Fixing Issues: If you want to contributte by fixing an issue, please check the eemont issues: contributions are welcome for open issues with labels bug and help wanted.

- **Enhancement**: New features and modules are welcome! You can check the eemont issues: contributions are welcome for open issues with labels enhancement and help wanted.

- **Documentation**: You can add examples, notes and references to the eemont documentation by using the NumPy Docstrings of the eemont documentation, or by creating blogs, tutorials or papers.


## Contribution Steps

First, fork the **ee_extra** repository and clone it to your local machine. Then, create a development branch:

```
git checkout -b name-of-dev-branch
```


