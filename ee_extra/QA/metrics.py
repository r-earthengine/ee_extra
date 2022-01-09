from abc import ABC, abstractmethod
from typing import Any, Dict, Type, List
import ee

from ee_extra.utils import _get_case_insensitive_close_matches


def listMetrics() -> Dict[str, Type["Metric"]]:
    """Get the name and class of all QA metrics.

    Returns:
        A dictionary of Metric subclasses with class names as keys and classes as
        values.
    """
    return {cls.__name__: cls for cls in Metric.__subclasses__()}


def getMetrics(names: List[str]) -> List[Type["Metric"]]:
    """Take a list of names and return a list of matching QA metrics.

    Args:
        names : A list or tuple of strings or a single string with the names of QA
            metrics.

    Returns:
        A list of Metric subclasses matching the input names.

    Raises:
        AttributeError : If at least one of the metrics is invalid.
    """
    names = [names] if not isinstance(names, (list, tuple)) else names

    options = listMetrics()
    keys = list(options.keys())
    selected = []

    for name in names:
        try:
            selected.append(options[name])
        except KeyError:
            close_matches = _get_case_insensitive_close_matches(name, keys, n=3)
            hint = " Close matches: {}.".format(close_matches) if close_matches else ""

            raise AttributeError(
                '"{}" is not a supported quality assessment metric. Choose from {}.{}'.format(
                    name, keys, hint
                )
            )

    return selected


class Metric(ABC):
    """The abstract class that is implemented by all quality assessment metrics."""

    def __new__(cls, original: ee.Image, modified: ee.Image, **kwargs: Any) -> None:
        """Calculate and return the QA metric value when the class is instantiated."""
        return cls._calculate(original, modified, **kwargs)

    @abstractmethod
    def _calculate(original: ee.Image, modified: ee.Image, **kwargs: Any) -> None:
        """Abstract method implemented by each Metric where the metric values are
        calculated between the input images. This should always be accessed indirectly
        by instantiating the Metric class rather than called.
        """
        return


class MSE(Metric):
    """Calculate band-wise Mean Squared Error (MSE) between an original and
    modified image with the same resolution and bands. A value of 0 represents no
    error.

    Args:
        original : The original image to use as a reference.
        modified : The modified image to compare to the original.
        kwargs : Additional keyword arguments passed to `ee.Image.reduceRegion`.

    Returns:
        A dictionary with band names as keys and MSE values as values.

    Examples:
        >>> from ee_extra.QA import metrics
        >>> bands = ["B4", "B3", "B2"]
        >>> img1 = ee.Image("COPERNICUS/S2_SR/20210703T170849_20210703T171938_T14SPG").select(bands)
        >>> img2 = ee.Image("COPERNICUS/S2_SR/20210708T170851_20210708T171925_T14SPG").select(bands)
        >>> metrics.MSE(img1, img2, bestEffort=True).getInfo()
        {'B2': 1329906.30450367, 'B3': 1175020.2097754816, 'B4': 1199736.6394475223}
    """

    @staticmethod
    def _calculate(
        original: ee.Image, modified: ee.Image, **kwargs: Any
    ) -> ee.Dictionary:
        mse = (
            original.subtract(modified)
            .pow(2)
            .reduceRegion(reducer=ee.Reducer.mean(), **kwargs)
        )

        return mse


class RMSE(Metric):
    """Calculate band-wise Root-Mean Squared Error (RMSE) between an original and
    modified image with the same resolution and bands. A value of 0 represents no
    error.

    Args:
        original : The original image to use as a reference.
        modified : The modified image to compare to the original.
        kwargs : Additional keyword arguments passed to `ee.Image.reduceRegion`.

    Returns:
        A dictionary with band names as keys and RMSE values as values.

    Examples:
        >>> from ee_extra.QA import metrics
        >>> bands = ["B4", "B3", "B2"]
        >>> img1 = ee.Image("COPERNICUS/S2_SR/20210703T170849_20210703T171938_T14SPG").select(bands)
        >>> img2 = ee.Image("COPERNICUS/S2_SR/20210708T170851_20210708T171925_T14SPG").select(bands)
        >>> metrics.RMSE(img1, img2, bestEffort=True).getInfo()
        {'B2': 1153.215636602136, 'B3': 1083.9834914681503, 'B4': 1095.3249013181078}
    """

    @staticmethod
    def _calculate(
        original: ee.Image, modified: ee.Image, **kwargs: Any
    ) -> ee.Dictionary:

        mse = MSE(original, modified, **kwargs)
        sqrt_vals = ee.Array(mse.values()).sqrt().toList()
        rmse = ee.Dictionary.fromLists(mse.keys(), sqrt_vals)

        return rmse


class RASE(Metric):
    """Calculate image-wise Relative Average Spectral Error (RASE) between an
    original and modified image with the same resolution and bands. A value of 0
    represents no error.

    Args:
        original : The original image to use as a reference.
        modified : The modified image to compare to the original.
        kwargs : Additional keyword arguments passed to `ee.Image.reduceRegion`.

    Returns:
        A dictionary with band names as keys and RASE values as values.

    References:
        Vaiopoulos, A. D. (2011). Developing Matlab scripts for image analysis
            and quality assessment. Earth Resources and Environmental Remote
            Sensing/GIS Applications II. https://doi.org/10.1117/12.897806

    Examples:
        >>> from ee_extra.QA import metrics
        >>> bands = ["B4", "B3", "B2"]
        >>> img1 = ee.Image("COPERNICUS/S2_SR/20210703T170849_20210703T171938_T14SPG").select(bands)
        >>> img2 = ee.Image("COPERNICUS/S2_SR/20210708T170851_20210708T171925_T14SPG").select(bands)
        >>> metrics.RASE(img1, img2, bestEffort=True).getInfo()
        125.72348999711838
    """

    @staticmethod
    def _calculate(
        original: ee.Image, modified: ee.Image, **kwargs: Any
    ) -> ee.Dictionary:

        mse = ee.Number(
            MSE(original, modified, **kwargs).values().reduce(ee.Reducer.mean())
        )
        xbar = (
            original.reduceRegion(ee.Reducer.mean(), **kwargs)
            .values()
            .reduce(ee.Reducer.mean())
        )
        rase = mse.sqrt().multiply(ee.Number(100).divide(xbar))
        return rase


class ERGAS(Metric):
    """Calculate image-wise Dimensionless Global Relative Error of Synthesis
    (ERGAS) between an original and modified image with the same resolution and bands.
    A value of 0 represents no error.

    Args:
        original : The original image to use as a reference.
        modified : The modified image to compare to the original.
        kwargs : Additional keyword arguments passed to `ee.Image.reduceRegion`.

    Returns:
        A dictionary with band names as keys and ERGAS values as values.

    References:
        Vaiopoulos, A. D. (2011). Developing Matlab scripts for image analysis
            and quality assessment. Earth Resources and Environmental Remote
            Sensing/GIS Applications II. https://doi.org/10.1117/12.897806

    Examples:
        >>> from ee_extra.QA import metrics
        >>> bands = ["B4", "B3", "B2"]
        >>> img1 = ee.Image("COPERNICUS/S2_SR/20210703T170849_20210703T171938_T14SPG").select(bands)
        >>> img2 = ee.Image("COPERNICUS/S2_SR/20210708T170851_20210708T171925_T14SPG").select(bands)
        >>> metrics.ERGAS(img1, img2, bestEffort=True).getInfo()
        3774.9270912567363
    """

    @staticmethod
    def _calculate(
        original: ee.Image, modified: ee.Image, **kwargs: Any
    ) -> ee.Dictionary:

        h = modified.projection().nominalScale()
        l = original.projection().nominalScale()
        msek = ee.Array(MSE(original, modified, **kwargs).values())
        xbark = ee.Array(original.reduceRegion(ee.Reducer.mean(), **kwargs).values())

        band_error = ee.Number(
            msek.divide(xbark).toList().reduce(ee.Reducer.mean())
        ).sqrt()
        ergas = band_error.multiply(h.divide(l).multiply(100))

        return ergas


class DIV(Metric):
    """Calculate band-wise Difference in Variance (DIV) between an original and
    modified image with the same resolution and bands. A value of 0 represents no
    change in variance.

    Args:
        original : The original image to use as a reference.
        modified : The modified image to compare to the original.
        kwargs : Additional keyword arguments passed to `ee.Image.reduceRegion`.

    Returns:
        A dictionary with band names as keys and DIV values as values.

    References:
        Vaiopoulos, A. D. (2011). Developing Matlab scripts for image analysis
            and quality assessment. Earth Resources and Environmental Remote
            Sensing/GIS Applications II. https://doi.org/10.1117/12.897806

    Examples:
        >>> from ee_extra.QA import metrics
        >>> bands = ["B4", "B3", "B2"]
        >>> img1 = ee.Image("COPERNICUS/S2_SR/20210703T170849_20210703T171938_T14SPG").select(bands)
        >>> img2 = ee.Image("COPERNICUS/S2_SR/20210708T170851_20210708T171925_T14SPG").select(bands)
        >>> metrics.DIV(img1, img2, bestEffort=True).getInfo()
        {'B2': -0.11554855234271111, 'B3': -0.053204512324202424, 'B4': -0.07635340111753797}
    """

    @staticmethod
    def _calculate(
        original: ee.Image, modified: ee.Image, **kwargs: Any
    ) -> ee.Dictionary:

        var_orig = ee.Array(
            original.reduceRegion(ee.Reducer.variance(), **kwargs).values()
        )
        var_mod = ee.Array(
            modified.reduceRegion(ee.Reducer.variance(), **kwargs).values()
        )

        div = var_mod.divide(var_orig).multiply(-1).add(1)
        return ee.Dictionary.fromLists(original.bandNames(), div.toList())


class bias(Metric):
    """Calculate band-wise bias between an original and modified image of the
    same spatial resolution. A value of 0 represents no bias.

    Args:
        original : The original image to use as a reference.
        modified : The modified image to compare to the original.
        kwargs : Additional keyword arguments passed to `ee.Image.reduceRegion`.

    Returns:
        A dictionary with band names as keys and bias values as values.

    References:
        Vaiopoulos, A. D. (2011). Developing Matlab scripts for image analysis
            and quality assessment. Earth Resources and Environmental Remote
            Sensing/GIS Applications II. https://doi.org/10.1117/12.897806

    Examples:
        >>> from ee_extra.QA import metrics
        >>> bands = ["B4", "B3", "B2"]
        >>> img1 = ee.Image("COPERNICUS/S2_SR/20210703T170849_20210703T171938_T14SPG").select(bands)
        >>> img2 = ee.Image("COPERNICUS/S2_SR/20210708T170851_20210708T171925_T14SPG").select(bands)
        >>> metrics.bias(img1, img2, bestEffort=True).getInfo()
        {'B2': -0.09946485586107534, 'B3': -0.06336055792360518, 'B4': -0.008140914735944804}
    """

    @staticmethod
    def _calculate(
        original: ee.Image, modified: ee.Image, **kwargs: Any
    ) -> ee.Dictionary:

        xbar = ee.Array(original.reduceRegion(ee.Reducer.mean(), **kwargs).values())
        ybar = ee.Array(modified.reduceRegion(ee.Reducer.mean(), **kwargs).values())

        bias = ybar.divide(xbar).multiply(-1).add(1)
        return ee.Dictionary.fromLists(original.bandNames(), bias.toList())


class CC(Metric):
    """Calculate band-wise correlation coefficient (CC) between an original and
    modified image with the same resolution and bands. A value of 1 represents
    perfect correlation.

    Args:
        original : The original image to use as a reference.
        modified : The modified image to compare to the original.
        kwargs : Additional keyword arguments passed to `ee.Image.reduceRegion`.

    Returns:
        A dictionary with band names as keys and CC values as values.

    References:
        Gonzalez, R. C., & Woods, R. E. (2018). Digital Image Processing. Pearson.

    Examples:
        >>> from ee_extra.QA import metrics
        >>> bands = ["B4", "B3", "B2"]
        >>> img1 = ee.Image("COPERNICUS/S2_SR/20210703T170849_20210703T171938_T14SPG").select(bands)
        >>> img2 = ee.Image("COPERNICUS/S2_SR/20210708T170851_20210708T171925_T14SPG").select(bands)
        >>> metrics.CC(img1, img2, bestEffort=True).getInfo()
        {'B2': 0.21228665943220423, 'B3': 0.02972520903338099, 'B4': 0.06995703183852472}
    """

    @staticmethod
    def _calculate(
        original: ee.Image, modified: ee.Image, **kwargs: Any
    ) -> ee.Dictionary:

        xbar = ee.Image.constant(
            original.reduceRegion(ee.Reducer.mean(), **kwargs).values()
        )
        ybar = ee.Image.constant(
            modified.reduceRegion(ee.Reducer.mean(), **kwargs).values()
        )

        x_center = original.subtract(xbar)
        y_center = modified.subtract(ybar)

        numerator = ee.Array(
            x_center.multiply(y_center)
            .reduceRegion(ee.Reducer.sum(), **kwargs)
            .values()
        )

        x_denom = ee.Array(
            x_center.pow(2).reduceRegion(ee.Reducer.sum(), **kwargs).values()
        )
        y_denom = ee.Array(
            y_center.pow(2).reduceRegion(ee.Reducer.sum(), **kwargs).values()
        )

        denom = x_denom.multiply(y_denom).sqrt()

        cc = numerator.divide(denom)

        return ee.Dictionary.fromLists(original.bandNames(), cc.toList())


class CML(Metric):
    """Calculate band-wise change in mean luminance (CML) between an original and
    modified image with the same resolution and bands. A value of 1 represents no
    change in luminance.

    Args:
        original : The original image to use as a reference.
        modified : The modified image to compare to the original.
        kwargs : Additional keyword arguments passed to `ee.Image.reduceRegion`.

    Returns:
        A dictionary with band names as keys and CML values as values.

    References:
        Wang, Z., & Bovik, A. C. (2002). A universal image quality index. IEEE
            Signal Processing Letters, 9(3), 81–84.
            https://doi.org/10.1109/97.995823

    Examples:
        >>> from ee_extra.QA import metrics
        >>> bands = ["B4", "B3", "B2"]
        >>> img1 = ee.Image("COPERNICUS/S2_SR/20210703T170849_20210703T171938_T14SPG").select(bands)
        >>> img2 = ee.Image("COPERNICUS/S2_SR/20210708T170851_20210708T171925_T14SPG").select(bands)
        >>> metrics.CML(img1, img2, bestEffort=True).getInfo()
        {'B2': 0.99552102740279, 'B3': 0.9981158806578726, 'B4': 0.9999671314230874}
    """

    @staticmethod
    def _calculate(
        original: ee.Image, modified: ee.Image, **kwargs: Any
    ) -> ee.Dictionary:
        xbar = ee.Array(original.reduceRegion(ee.Reducer.mean(), **kwargs).values())
        ybar = ee.Array(modified.reduceRegion(ee.Reducer.mean(), **kwargs).values())

        l = xbar.multiply(ybar).multiply(2).divide(xbar.pow(2).add(ybar.pow(2)))

        return ee.Dictionary.fromLists(original.bandNames(), l.toList())


class CMC(Metric):
    """Calculate band-wise change in mean contrast (CMC) between an original and
    modified image with the same resolution and bands. A value of 1 represents no
    change in contrast.

    Args:
        original : The original image to use as a reference.
        modified : The modified image to compare to the original.
        kwargs : Additional keyword arguments passed to `ee.Image.reduceRegion`.

    Returns:
        A dictionary with band names as keys and CMC values as values.

    References:
        Wang, Z., & Bovik, A. C. (2002). A universal image quality index. IEEE
            Signal Processing Letters, 9(3), 81–84.
            https://doi.org/10.1109/97.995823

    Examples:
        >>> from ee_extra.QA import metrics
        >>> bands = ["B4", "B3", "B2"]
        >>> img1 = ee.Image("COPERNICUS/S2_SR/20210703T170849_20210703T171938_T14SPG").select(bands)
        >>> img2 = ee.Image("COPERNICUS/S2_SR/20210708T170851_20210708T171925_T14SPG").select(bands)
        >>> metrics.CMC(img1, img2, bestEffort=True).getInfo()
        {'B2': 0.9985072836552178, 'B3': 0.9996642040598637, 'B4': 0.9993236505770505}
    """

    @staticmethod
    def _calculate(
        original: ee.Image, modified: ee.Image, **kwargs: Any
    ) -> ee.Dictionary:
        xvar = ee.Array(original.reduceRegion(ee.Reducer.variance(), **kwargs).values())
        yvar = ee.Array(modified.reduceRegion(ee.Reducer.variance(), **kwargs).values())
        xsd = ee.Array(original.reduceRegion(ee.Reducer.stdDev(), **kwargs).values())
        ysd = ee.Array(modified.reduceRegion(ee.Reducer.stdDev(), **kwargs).values())

        c = xsd.multiply(ysd).multiply(2).divide(xvar.add(yvar))

        return ee.Dictionary.fromLists(original.bandNames(), c.toList())


class UIQI(Metric):
    """Calculate band-wise Universal Image Quality Index (UIQI) between an
    original and modified image with the same resolution and bands. A value of 1
    represents perfect quality.

    Args:
        original : The original image to use as a reference.
        modified : The modified image to compare to the original.
        kwargs : Additional keyword arguments passed to `ee.Image.reduceRegion`.

    Returns:
        A dictionary with band names as keys and UIQI values as values.

    References:
        Wang, Z., & Bovik, A. C. (2002). A universal image quality index. IEEE
            Signal Processing Letters, 9(3), 81–84.
            https://doi.org/10.1109/97.995823

    Examples:
        >>> from ee_extra.QA import metrics
        >>> bands = ["B4", "B3", "B2"]
        >>> img1 = ee.Image("COPERNICUS/S2_SR/20210703T170849_20210703T171938_T14SPG").select(bands)
        >>> img2 = ee.Image("COPERNICUS/S2_SR/20210708T170851_20210708T171925_T14SPG").select(bands)
        >>> metrics.UIQI(img1, img2, bestEffort=True).getInfo()
        {'B2': 0.06990741860751772, 'B3': 0.029659240394113433, 'B4': 0.2110203688492463}
    """

    @staticmethod
    def _calculate(
        original: ee.Image, modified: ee.Image, **kwargs: Any
    ) -> ee.Dictionary:
        cc = ee.Array(CC(original, modified, **kwargs).values())
        l = ee.Array(CMC(original, modified, **kwargs).values())
        c = ee.Array(CML(original, modified, **kwargs).values())

        uiqi = cc.multiply(l).multiply(c)

        return ee.Dictionary.fromLists(original.bandNames(), uiqi.toList())
