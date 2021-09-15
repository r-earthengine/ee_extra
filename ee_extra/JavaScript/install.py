"""JavaScript install module provide functions to install/uninstall
a JavaScript Earth Enginemodule.
"""


import pathlib
import re

import pkg_resources
import requests


def _convert_path_to_ee_sources(path: str) -> str:
    """Get the remote module path from the 'ee-sources' GCS bucket.

    Args:
        path: str

    Returns:
        An ee-sources module url.
    """
    bpath = path.replace(":", "/")
    eempath = f"https://storage.googleapis.com/ee-sources/{bpath}"
    return eempath


def _get_ee_sources_path() -> str:
    """Gets the ee-sources folder path.

    Returns:
        The ee-sources folder path.
    """
    ee_extra_py_file = pkg_resources.resource_filename("ee_extra", "ee_extra.py")
    pkgdir = pathlib.Path(ee_extra_py_file).parent
    return pkgdir.joinpath("ee-sources").as_posix()


def _convert_path_to_ee_extra(path: str) -> str:
    """Convert an Earth Engine module path into an ee_extra module path.

    Args:
        path: str

    Returns:
        An ee_extra modules path.
    """
    if path.endswith(".js"):
        ee_extra_path = pathlib.Path(_get_ee_sources_path()).joinpath(
            path.replace(":", "/")
        )
    else:
        ee_extra_path = pathlib.Path(_get_ee_sources_path()).joinpath(
            path.replace(":", "/") + ".js"
        )

    return ee_extra_path


def _check_if_module_exists(path: str) -> bool:
    """Check if an Earth Engine module has been installed in ee_extra.

    Args:
        path: str

    Returns:
        Whether the module has been installed.
    """
    return pathlib.Path(_convert_path_to_ee_extra(path)).exists()


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


def _install(x: str, update: bool, quiet: bool = False):
    """Install an Earth Engine JavaScript module.

    The specified module will be installed in the ee_extra module path.

    Args:
        x: str
        update: bool
    """
    if _check_if_module_exists(x) and not update:

        quiet or print(f"The module '{x}' is already installed!")

    else:

        quiet or print(f"Downloading '{x}'...")

        ee_sources = _get_ee_sources_path()

        # Local path
        module_folder = pathlib.Path(ee_sources).joinpath(
            "/".join(x.replace(":", "/").split("/")[:-1])
        )

        if not module_folder.exists():
            module_folder.mkdir(parents=True, exist_ok=True)
        r = requests.get(_convert_path_to_ee_sources(x))

        open(_convert_path_to_ee_extra(x), "wb").write(r.content)

        quiet or print(f"The module '{x}' was successfully installed!")


def install(x: str, update: bool = False,quiet: bool = False) -> list:
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

                    _install(dep, update, quiet)
                    quiet or print(f"Checking dependencies for {dep}...")
                    x.extend(_get_dependencies(dep))
                    installed.append(dep)
                    x = [item for item in x if item not in installed]
                    _install_dependencies(x, update, installed)

        else:

            quiet or print(f"All dependencies were successfully installed!")

    return _install_dependencies(deps, update, [])


def rmtree(path):
    """Iterative delete of files using pathlib"""
    for p in path.iterdir():
        if p.is_dir():
            rmtree(p)
        else:
            p.unlink()
    path.rmdir()


def uninstall(x: str, quiet: bool = False):
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
        rmtree(_convert_path_to_ee_extra(x).parent)
        quiet or print(f"The module '{x}' was successfully uninstalled!")
    else:
        quiet or print(f"The module '{x}' is not installed!")
