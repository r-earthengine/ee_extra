from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Sequence, Type, TypeVar, Union

import ee

from ee_extra.QA.metrics import getMetrics
from ee_extra.Spectral.core import matchHistogram
from ee_extra.STAC.utils import _get_platform_STAC
from ee_extra.utils import _filter_image_bands, _get_case_insensitive_close_matches

ImageLike = TypeVar("ImageLike", ee.Image, ee.ImageCollection)

L7_BANDS = {"sharpenable": ["B1", "B2", "B3", "B4", "B5", "B7"], "pan": "B8"}
L8_BANDS = {"sharpenable": ["B2", "B3", "B4", "B5", "B6", "B7"], "pan": "B8"}
PLATFORM_BANDS = {
    "LANDSAT/LC08/C01/T1_TOA": L8_BANDS,
    "LANDSAT/LC08/C01/T1_RT_TOA": L8_BANDS,
    "LANDSAT/LC08/C01/T2_TOA": L8_BANDS,
    "LANDSAT/LC08/C01/T1_RT": L8_BANDS,
    "LANDSAT/LO08/C01/T1": L8_BANDS,
    "LANDSAT/LC08/C01/T1": L8_BANDS,
    "LANDSAT/LO08/C01/T2": L8_BANDS,
    "LANDSAT/LC08/C01/T2": L8_BANDS,
    "LANDSAT/LE07/C01/T1_TOA": L7_BANDS,
    "LANDSAT/LE07/C01/T1_RT_TOA": L7_BANDS,
    "LANDSAT/LE07/C01/T2_TOA": L7_BANDS,
    "LANDSAT/LE07/C01/T1_RT": L7_BANDS,
    "LANDSAT/LE07/C01/T1": L7_BANDS,
    "LANDSAT/LE07/C01/T2": L7_BANDS,
}


def _panSharpen(
    img: ImageLike,
    method: str,
    qa: Optional[Union[str, List[str]]] = None,
    prefix: str = "ee_extra",
    **kwargs: Any
) -> ImageLike:
    """Apply panchromatic sharpening to an Image or ImageCollection.

    Args:
        source : Image or ImageCollection to sharpen.
        method : The sharpening algorithm to apply. Current options are "SFIM" (Smoothing
            Filter-based Intensity Modulation), "HPFA" (High Pass Filter Addition), "PCS"
            (Principal Component Substitution), and "SM" (simple mean).
        qa : One or more optional quality metrics to calculate and set as properties on
            the sharpened image. See ee_extra.QA.metrics.listMetrics().keys() for a list
            of supported metrics.
        prefix : A prefix for any new properties. For example, quality metrics will be
            set as `prefix:metric`, e.g. `ee_extra:RMSE`.
        **kwargs : Keyword arguments passed to ee.Image.reduceRegion() such as
            "geometry", "maxPixels", "bestEffort", etc. These arguments are only used for
            PCS sharpening and quality assessments.

    Returns:
        The Image or ImageCollection with all sharpenable bands sharpened to the panchromatic resolution.
    """

    def get_platform_bands(img: ee.Image) -> Dict[str, Sequence[str]]:
        """Get the correct platform bands for sharpening supported platforms.

        Args:
            source : An Image or ImageCollection identify a platform function for.

        Returns:
            A function that accepts Images and ImageCollections from the source platform.

        Raises:
            AttributeError : If the platform is unsupported.
        """
        platform = _get_platform_STAC(img)["platform"]
        platform_options = list(PLATFORM_BANDS.keys())

        try:
            return PLATFORM_BANDS[platform]
        except KeyError:
            raise AttributeError(
                "Sharpening is not supported for the {} platform. Use one of the following platforms: {}".format(
                    platform, platform_options
                )
            )

    def apply_sharpening(img: ee.Image) -> ee.Image:
        """Identify and apply the correct sharpening algorithm to an Image.

        Args:
            img : Image to sharpen.

        Returns:
            The Image with all sharpenable bands sharpened to the panchromatic resolution.
        """
        source = _filter_image_bands(img, platform_bands["sharpenable"])
        pan = img.select(platform_bands["pan"])

        sharpened: ee.Image = sharpener(source, pan, **kwargs)

        sharpened = ee.Image(sharpened.copyProperties(source, pan.propertyNames()))
        sharpened = sharpened.updateMask(source.mask())

        if qa is not None:
            sharpened = run_and_set_qa(source, sharpened, qa)

        return sharpened

    def run_and_set_qa(
        original: ee.Image, modified: ee.Image, qa: Union[str, List[str]]
    ) -> ee.Image:
        """Get any valid requested quality assessment functions and run each of them to assess the quality of the
        sharpened Image. Set the results of each quality assessment as a new property with the format `prefix:metric`.

        Args
            original : The original, pre-sharpened image.
            modified : The sharpened image.
            qa : Names of one or more metrics to calculate.

        Returns:
            The modified image with a new property set for each quality assessment.
        """
        selected_metrics = getMetrics(qa)

        original = original.select(modified.bandNames())

        for metric in selected_metrics:
            values = metric(original, modified, reproject=True, **kwargs)
            prop = "{}:{}".format(prefix, metric.__name__)

            modified = modified.set(prop, values)

        return modified

    sharpener = getSharpener(method)
    platform_bands = get_platform_bands(img)

    if isinstance(img, ee.image.Image):
        sharpened = apply_sharpening(img)
    elif isinstance(img, ee.imagecollection.ImageCollection):
        sharpened = img.map(apply_sharpening)

    return sharpened


def listSharpeners() -> Dict[str, Type["Sharpener"]]:
    """Get the name and class of all pan-sharpening algorithms.

    Returns:
        A dictionary of Sharpener subclasses with class names as keys and classes as
        values.
    """
    sharpeners: List[Type[Sharpener]] = Sharpener.__subclasses__()
    return {sharpener.__name__: sharpener for sharpener in sharpeners}


def getSharpener(name: str) -> Type["Sharpener"]:
    """Return a pan-sharpening algorithm that matches a name.

    Args:
        name : The name of a sharpener, e.g. SFIM.

    Returns:
        The Sharpener subclass.
    """
    options = listSharpeners()
    keys = list(options.keys())

    try:
        sharpener = options[name]
    except KeyError:
        close_matches = _get_case_insensitive_close_matches(name, keys, n=3)
        hint = " Close matches: {}.".format(close_matches) if close_matches else ""

        raise AttributeError(
            '"{}" is not a supported sharpening algorithm. Choose from {}.{}'.format(
                name, keys, hint
            )
        )
    return sharpener


class Sharpener(ABC):
    """The abstract class that is implemented by all sharpening algorithms."""

    def __new__(cls, img: ee.Image, pan: ee.Image, **kwargs: Any) -> ee.Image:
        """Apply pansharpening and return the sharpened image when the class is
        instantiated.
        """
        return cls._sharpen(img, pan, **kwargs)

    @staticmethod
    @abstractmethod
    def _sharpen(img: ee.Image, pan: ee.Image, **kwargs: Any) -> ee.Image:
        """Abstract method implemented by each Sharpener that applies sharpening."""
        return


class SFIM(Sharpener):
    """The Smoothing Filter-based Intensity Modulation (SFIM) sharpener."""

    @staticmethod
    def _sharpen(img: ee.Image, pan: ee.Image, **kwargs: Any) -> ee.Image:
        """Apply Smoothing Filter-based Intensity Modulation (SFIM) sharpening.

        Args:
            img : Image to sharpen with only sharpenable bands selected.
            pan : Image with only the panchromatic band selected.
            kwargs : Additional keyword arguments. Currently unused.

        Returns:
            The Image with all sharpenable bands sharpened to the panchromatic
            resolution.

        References:
            Liu, J. G. (2000). Smoothing Filter-based Intensity Modulation: A
                spectral preserve image fusion technique for improving spatial
                details. International Journal of Remote Sensing, 21(18), 3461–3472.
                https://doi.org/10.1080/014311600750037499
        """
        img_scale = img.projection().nominalScale()
        pan_scale = pan.projection().nominalScale()
        kernel_width = img_scale.divide(pan_scale)
        kernel = ee.Kernel.square(radius=kernel_width.divide(2))
        pan_smooth = pan.reduceNeighborhood(reducer=ee.Reducer.mean(), kernel=kernel)

        img = img.resample("bicubic")
        sharp = img.multiply(pan).divide(pan_smooth)
        sharp = sharp.reproject(pan.projection())
        return sharp


class HPFA(Sharpener):
    """The High Pass Filter Addition (HPFA) sharpener."""

    @staticmethod
    def _sharpen(img: ee.Image, pan: ee.Image, **kwargs: Any) -> ee.Image:
        """Apply High-Pass Filter Addition sharpening.

        Args:
            img : Image to sharpen with only sharpenable bands selected.
            pan : Image with only the panchromatic band selected.
            kwargs : Additional keyword arguments. Currently unused.

        Returns:
            The Image with all sharpenable bands sharpened to the panchromatic
            resolution.

        References:
            Gangkofner, U. G., Pradhan, P. S., & Holcomb, D. W. (2008). Optimizing
                the High-Pass Filter Addition Technique for Image Fusion.
                Photogrammetric Engineering & Remote Sensing, 74(9), 1107–1118.
                https://doi.org/10.14358/pers.74.9.1107
        """
        img_scale = img.projection().nominalScale()
        pan_scale = pan.projection().nominalScale()
        kernel_width = img_scale.divide(pan_scale).multiply(2).add(1)

        img = img.resample("bicubic")

        center_val = kernel_width.pow(2).subtract(1)
        center = kernel_width.divide(2).int()
        kernel_row = ee.List.repeat(-1, kernel_width)
        kernel = ee.List.repeat(kernel_row, kernel_width)
        kernel = kernel.set(center, ee.List(kernel.get(center)).set(center, center_val))
        kernel = ee.Kernel.fixed(weights=kernel, normalize=True)

        pan_hpf = pan.convolve(kernel)
        sharp = img.add(pan_hpf)
        sharp = sharp.reproject(pan.projection())

        return sharp


class PCS(Sharpener):
    """The Principal Component Substitution (PCS) sharpener."""

    @staticmethod
    def _sharpen(img: ee.Image, pan: ee.Image, **kwargs: Any) -> ee.Image:
        """Apply Principal Component Substitution (PCS) sharpening.

        Args:
            img : Image to sharpen with only sharpenable bands selected.
            pan : Image with only the panchromatic band selected.

        Returns:
            The Image with all sharpenable bands sharpened to the panchromatic
            resolution.
        """
        img = img.resample("bicubic").reproject(pan.projection())
        band_names = img.bandNames()

        band_means = img.reduceRegion(ee.Reducer.mean(), **kwargs)
        img_means = band_means.toImage(band_names)
        img_centered = img.subtract(img_means)

        img_arr = img_centered.toArray()
        covar = img_arr.reduceRegion(ee.Reducer.centeredCovariance(), **kwargs)
        covar_arr = ee.Array(covar.get("array"))
        eigens = covar_arr.eigen()
        eigenvectors = eigens.slice(1, 1)
        img_arr_2d = img_arr.toArray(1)

        principal_components = (
            ee.Image(eigenvectors)
            .matrixMultiply(img_arr_2d)
            .arrayProject([0])
            .arrayFlatten([band_names])
        )

        pc1_name = principal_components.bandNames().get(0)

        # A dictionary can't use an ee.ComputedObject as a key, so set temporary band names
        pc1 = principal_components.select([pc1_name]).rename(["PC1"])
        pan = pan.rename(["pan"])

        pan_matched = matchHistogram(
            source=pan,
            target=pc1,
            bands={"pan": "PC1"},
            geometry=kwargs.get("geometry"),
        ).rename([pc1_name])

        principal_components = principal_components.addBands(
            pan_matched, overwrite=True
        )

        sharp_centered = (
            ee.Image(eigenvectors)
            .matrixSolve(principal_components.toArray().toArray(1))
            .arrayProject([0])
            .arrayFlatten([band_names])
        )
        sharp = sharp_centered.add(img_means)

        return sharp


class SM(Sharpener):
    """The Simple Mean (SM) sharpener."""

    @staticmethod
    def _sharpen(img: ee.Image, pan: ee.Image, **kwargs: Any) -> ee.Image:
        """Apply Simple Mean (SM) sharpening.

        Args:
            img : Image to sharpen with only sharpenable bands selected.
            pan : Image with only the panchromatic band selected.
            kwargs : Additional keyword arguments. Currently unused.

        Returns:
            The Image with all sharpenable bands sharpened to the panchromatic
            resolution.
        """
        img = img.resample("bicubic")
        sharp = img.add(pan).multiply(0.5)
        sharp = sharp.reproject(pan.projection())
        return sharp
