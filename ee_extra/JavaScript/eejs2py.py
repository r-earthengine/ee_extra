"""JavaScript module provide functions to evaluate JS 
code in the EE session. The following functions are
implemented:

I. Evaluate JS code

- evaluate: Evaluate a JS string code.
"""

import json
import os
import re

import ee
import pkg_resources
import requests
from ee_extra import Extra
from js2py import EvalJs


def _convert_path_to_ee_sources(path: str) -> str:
    """Convert an Earth Engine module path into an ee-sources module url.

    Args:
        path: str

    Returns:
        An ee-sources module url.
    """
    return os.path.join("https://storage.googleapis.com/ee-sources/", path.replace(":", "/"))


def _get_ee_sources_path() -> str:
    """Gets the ee-sources folder path.

    Returns:
        The ee-sources folder path.
    """
    pkgdir = os.path.dirname(pkg_resources.resource_filename("ee_extra", "ee_extra.py"))

    return os.path.join(pkgdir, "ee-sources")


def _convert_path_to_ee_extra(path: str) -> str:
    """Convert an Earth Engine module path into an ee_extra module path.

    Args:
        path: str

    Returns:
        An ee_extra modules path.
    """
    if path.endswith(".js"):

        ee_extra_path = os.path.join(_get_ee_sources_path(), path.replace(":", "/"))

    else:

        ee_extra_path = os.path.join(_get_ee_sources_path(), path.replace(":", "/") + ".js")

    return ee_extra_path


def _check_if_module_exists(path: str) -> bool:
    """Check if an Earth Engine module has been installed in ee_extra.

    Args:
        path: str

    Returns:
        Whether the module has been installed.
    """
    return os.path.exists(_convert_path_to_ee_extra(path))


def _open_module_as_str(path: str) -> str:
    """Open a module as a string.

    Args:
        path: str

    Returns:
        Specified module as a string.
    """
    if _check_if_module_exists(path):

        with open(_convert_path_to_ee_extra(path), "r") as file:
            module = file.read()

        return module

    else:

        raise Exception(f"The module '{path}' is not installed!")


def _get_dependencies(path: str) -> list:
    """Get the dependencies of an Earth Engine module.

    Args:
        path: str

    Returns:
        List of dependencies.
    """
    if _check_if_module_exists(path):

        module = _open_module_as_str(path)

        dependencies = re.findall(r"require\((.*?)\)", module)
        dependenciesClean = []

        for dep in dependencies:
            dependenciesClean.append(dep.replace('"', "").replace("'", ""))

        return dependenciesClean

    else:

        raise Exception(f"The module '{path}' is not installed!")


def _install(x: str, update: bool):
    """Install an Earth Engine JavaScript module.

    The specified module will be installed in the ee_extra module path.

    Args:
        x: str
        update: bool
    """
    if _check_if_module_exists(x) and not update:

        print(f"The module '{x}' is already installed!")

    else:

        print(f"Downloading '{x}'...")

        ee_sources = _get_ee_sources_path()
        # module_folder = os.path.join(ee_sources, x.split(":")[0])
        module_folder = os.path.join(ee_sources, "/".join(x.replace(":", "/").split("/")[:-1]))

        if not os.path.isdir(module_folder):
            os.makedirs(module_folder)

        r = requests.get(_convert_path_to_ee_sources(x))

        open(_convert_path_to_ee_extra(x), "wb").write(r.content)

        print(f"The module '{x}' was successfully installed!")


# @Extra.add("JavaScript", "eejs2py", "install")
def install(x: str, update: bool = False) -> list:
    """Install an Earth Engine modue and its dependencies.

    The specified dependencies will be installed in the ee_extra module path.

    Args:
        x: str
        update: bool

    Examples:
        >>> import ee
        >>> from ee_extra import Extra
        >>> ee.Initialize()
        >>> Extra.JavaScript.eejs2py.install("users/dmlmont/spectral:spectral")
    """
    deps = [x]

    def _install_dependencies(x: list, update: bool, installed: list):

        if len(x) > 0:

            for dep in x:

                if dep not in installed:

                    _install(dep, update)
                    print(f"Checking dependencies for {dep}...")
                    x.extend(_get_dependencies(dep))
                    installed.append(dep)
                    x = [item for item in x if item not in installed]
                    _install_dependencies(x, update, installed)

        else:

            print(f"All dependencies were successfully installed!")

    return _install_dependencies(deps, update, [])


# @Extra.add("JavaScript", "eejs2py", "uninstall")
def uninstall(x: str):
    """Uninstall an Earth Engine JavaScript module.

    The specified module will be uninstalled. Dependencies won't be uninstalled.

    Args:
        x: str

    Examples:
        >>> import ee
        >>> from ee_extra import Extra
        >>> ee.Initialize()
        >>> Extra.JavaScript.eejs2py.uninstall("users/dmlmont/spectral:spectral")
    """
    if _check_if_module_exists(x):

        os.remove(_convert_path_to_ee_extra(x))

        print(f"The module '{x}' was successfully uninstalled!")

    else:

        print(f"The module '{x}' is not installed!")


# @Extra.add("JavaScript", "eejs2py", "junction")
def junction(x: str) -> str:
    """Evaluate an Earth Engine module.

    Returns an EvalJs object hosting all EE objects evaluated
    in the Earth Engine module.
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
    module = re.sub(re.compile("//.*?\n"), "", module)

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
                newText = re.sub(re.compile("//.*?\n"), "", newText)
                newText = newText.replace("exports", f"eeExtraExports{counter}")
                newLines.append("var eeExtraExports" + str(counter) + " = {};")
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


def _junction(x: str) -> str:
    """Evaluate an Earth Engine module.

    Returns an EvalJs object hosting all EE objects evaluated
    in the Earth Engine module.
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
    module = re.sub(re.compile("//.*?\n"), "", module)

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
                newText = re.sub(re.compile("//.*?\n"), "", newText)
                newText = newText.replace("exports", f"eeExtraExports{counter}")
                newLines.append("var eeExtraExports" + str(counter) + " = {};")
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


# @Extra.add("JavaScript", "eejs2py", "require")
def require(x: str) -> EvalJs:
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
    x = _junction(x)

    # 1. Replace arrays for EE Objects
    # --------------------------------
    # EE doesn't recognize JS Arrays directly,
    ## therefore, they are evaluated outside
    # lists = re.findall(r'\[(.*?)\]', x)
    # listsFull = []
    #
    # for l in lists:
    #    try:
    #        listsFull.append(list(map(float,l.split(","))))
    #    except:
    #        listsFull.append(l.replace('"',"").replace("'","").split(","))
    #
    # listsBrackets = {}
    # counter = 0
    #
    # for i in lists:
    #    listsBrackets["eeExtraObject" + str(counter)] = "[" + i + "]"
    #    counter += 1
    #
    # for key, value in listsBrackets.items():
    #    x = x.replace(value, key)
    #
    listsToEval = {}
    # counter = 0
    #
    # for i in listsFull:
    #    listsToEval["eeExtraObject" + str(counter)] = ee.List(i)
    #    counter += 1

    # 2. Add EE to the context
    # ------------------------
    # EvalJS doesn't know what ee is,
    # therefore, we have to give it as a context
    listsToEval["ee"] = ee
    listsToEval["exports"] = {}

    # 3. Evaluate the JS code
    # -----------------------
    # Give all the context needed and
    # evaluate the JS code
    context = EvalJs(listsToEval)
    context.execute(x)

    return context


# @Extra.add("JavaScript", "eejs2py", "evaluate")
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
