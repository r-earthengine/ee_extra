import io
import os
import re

from setuptools import find_packages, setup


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type("")
    with io.open(filename, mode="r", encoding="utf-8") as fd:
        return re.sub(text_type(r":[a-z]+:`~?(.*?)`"), text_type(r"``\1``"), fd.read())


setup(
    name="ee_extra",
    version="0.0.14",
    url="https://github.com/r-earthengine/ee_extra",
    license="Apache 2.0",
    author="Cesar Aybar, David Montero Loaiza and Aaron Zuspan",
    author_email="dml.mont@gmail.com",
    description="A ninja Python package behind rgee, rgeeExtra and eemont.",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=("tests",), include=["ee_extra", "ee_extra.*"]),
    package_data={"ee_extra": ["data/*.json"]},
    install_requires=[
        "earthengine-api",
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
