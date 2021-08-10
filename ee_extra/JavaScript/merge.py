"""Merge Javascript module in one file"""

import ee
import re
import pathlib
import sys
from js2py import EvalJs
from ee_extra.JavaScript.install import (
    _open_module_as_str,
    _get_ee_sources_path,
    _convert_path_to_ee_extra,
)
from box import Box
from ee_extra.JavaScript.utils import translate


def evaluate(x: str) -> EvalJs:
    """Evaluate a JS code inside the Earth Engine session.

    Returns an EvalJs object hosting all EE objects evaluated.
    The EE objects can be accessed using dot notation.

    Args:
        x: str

    Returns:
        An EvalJs object hosting all EE objects evaluated.

    Examples:
        >>> import ee
        >>> from ee_extra import Extra
        >>> ee.Initialize()
        >>> jscode = "var S2 = ee.ImageCollection('COPERNICUS/S2_SR').first()"
        >>> js = Extra.javaScript.eejs2py.evaluate(jscode)
        >>> js.S2
        <ee.image.Image at 0x7fe082c40e80>
    """

    # 1. Replace arrays for EE Objects
    # --------------------------------
    # EE doesn't recognize JS Arrays directly,
    # therefore, they are evaluated outside
    lists = re.findall(r"\[(.*?)\]", x)
    listsFull = []

    for l in lists:
        try:
            listsFull.append(list(map(float, l.split(","))))
        except:
            listsFull.append(l.replace('"', "").replace("'", "").split(","))

    listsBrackets = {}
    counter = 0

    for i in lists:
        listsBrackets["eeExtraObject" + str(counter)] = "[" + i + "]"
        counter += 1

    for key, value in listsBrackets.items():
        x = x.replace(value, key)

    listsToEval = {}
    counter = 0

    for i in listsFull:
        listsToEval["eeExtraObject" + str(counter)] = ee.List(i)
        counter += 1

    # 2. Add EE to the context
    # ------------------------
    # EvalJS doesn't know what ee is,
    # therefore, we have to give it as a context
    listsToEval["ee"] = ee

    # 3. Evaluate the JS code
    # -----------------------
    # Give all the context needed and
    # evaluate the JS code
    context = EvalJs(listsToEval)
    context.execute(x)

    return context


def junction(x: str) -> str:
    """Evaluate an Earth Engine module.

    Returns an EvalJs object hosting all EE objects evaluated in the Earth Engine module.
    The EE objects can be accessed using dot notation.

    Args:
        x: str

    Returns:
        An EvalJs object hosting all EE objects evaluated in the Earth Engine module.

    Examples:
        >>> import ee
        >>> from ee_extra import Extra
        >>> ee.Initialize()
        >>> spectral = Extra.JavaScript.eejs2py.require("users/dmlmont/spectral:spectral")
    """
    module = _open_module_as_str(x)

    module = re.sub(re.compile("/\*.*?\*/", re.DOTALL), "", module)
    # module = re.sub(re.compile("//.*?\n"), "", module)

    lines = module.split("\n")

    counter = 0

    while any([line for line in lines if "require(" in line]):

        newLines = []

        for line in lines:
            if "require(" in line:
                var = re.findall(r"var(.*?)=", line)[0].replace(" ", "")
                newText = _open_module_as_str(
                    re.findall(r"require\((.*?)\)", line)[0].replace('"', "").replace("'", "")
                )
                newText = re.sub(re.compile("/\*.*?\*/", re.DOTALL), "", newText)
                # newText = re.sub(re.compile("//.*?\n"), "", newText)
                newText = newText.replace("exports", f"eeExtraExports{counter}")
                newLines.append("var eeExtraExports" + str(counter) + " = UserDict();")
                newLines.extend(newText.split("\n"))
                newLines.append(f"var {var} = eeExtraExports{counter}")
                counter += 1
            else:
                newLines.append(line)

            lines = newLines

    # replacing nested double quotes
    raw_file = "\n".join(lines)
    regex_exp = r'(:\s+")(.*(?:\n(?!\s*"[^"\n:]+":).*)*)",$'
    final_file = re.sub(
        pattern=regex_exp,
        repl=lambda x: '{}{}",'.format(x.group(1), x.group(2).replace('"', "'")),
        string=raw_file,
        flags=re.M,
    )

    return final_file


def _convert_path_to_ee_extra_python_module(path: str) -> str:
    """Convert an Earth Engine module path into an ee_extra python module path to import it later.

    Args:
        path: str

    Returns:
        An ee_extra python module path.
    """
    path = _convert_path_to_ee_extra(path)
    path = "/".join(str(path).split("/")[:-1]) + "/module.py"

    return path


def _check_if_python_module_exists(path: str) -> bool:
    """Check if an Earth Engine python module has been created from a JavaScript module in ee_extra.

    Args:
        path: str

    Returns:
        Whether the python module has been created.
    """
    return pathlib.Path(_convert_path_to_ee_extra_python_module(path)).exists()


def require(x: str):
    """Require a JavaScript module as a python module.

    Args:
        path: str

    Returns:
        A python module.
    """
    module = translate(junction(x))    

    exports = dict()

    exec(module,exports)

    class BoxDict(Box):

        def __repr__(self):
            keys = list(self.keys())
            toShow = dict()
            for key in keys:
                toShow[key] = type(self[key])
            return str(toShow)

    return BoxDict(exports["exports"], frozen_box = True)


if __name__ == "__main__":
    from ee_extra.JavaScript.install import install

    jscode = "users/dmlmont/spectral:spectral"
    install(jscode)
    jscode_sf = require(jscode)
    jscode_sf.ee
