"""Merge Javascript module in one file"""

import pathlib
import re
import sys
from types import SimpleNamespace

import ee

from ee_extra.JavaScript.install import (
    _convert_path_to_ee_extra,
    _get_ee_sources_path,
    _open_module_as_str,
)
from ee_extra import translate


class JSModule(SimpleNamespace):
    """Creates a JSModule object.

    This class is used to store the exports of an Earth Engine JavaScript Module.
    """

    def __repr__(self):
        keys = list(self.__dict__.keys())
        toShow = dict()
        for key in keys:
            toShow[key] = type(self.__dict__[key])
        return str(toShow)


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
                    re.findall(r"require\((.*?)\)", line)[0]
                    .replace('"', "")
                    .replace("'", "")
                )
                newText = re.sub(re.compile("/\*.*?\*/", re.DOTALL), "", newText)
                # newText = re.sub(re.compile("//.*?\n"), "", newText)
                newText = newText.replace("exports", f"eeExtraExports{counter}")
                newLines.append("var eeExtraExports" + str(counter) + " = AttrDict();")
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
    # x = junction(x)
    module = translate(junction(x))

    exports = dict()

    exec(module, exports)

    return JSModule(**exports["exports"])
