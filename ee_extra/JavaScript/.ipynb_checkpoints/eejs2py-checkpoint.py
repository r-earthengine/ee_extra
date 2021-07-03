"""JavaScript module provide functions to evaluate JS 
code in the EE session. The following functions are
implemented:

I. Evaluate JS code

- evalJS: Evaluate a JS string code.
"""

import ee
import re
from ee_extra import Extra
from js2py import EvalJs
import requests
import pkg_resources
import os


def _convert_path_to_ee_sources(path: str) -> str:
    """Convert an Earth Engine module path into an ee-sources module url.

    Args:
        path: str
    Returns:
        An ee-sources module url.
    """    
    return os.path.join("https://storage.googleapis.com/ee-sources/", path.replace(":","/"))


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
    return os.path.join(_get_ee_sources_path(), path + ".js")


def _check_if_module_exists(path: str) -> bool:
    """Check if the specified module has been installed in ee_extra.

    Args:
        path: str
    Returns:
        Whether the module has been installed.
    """
    return os.path.exists(_convert_path_to_ee_extra(path))


@Extra.add("JavaScript", "eejs2py", "install")
def install(x: str):
    """Install an Earth Engine JavaScript module.

    The specified module will be installed in the ee_extra module path.

    Args:
        x: str    

    Examples:
        >>> import ee
        >>> from ee_extra import Extra
        >>> ee.Initialize()
        >>> Extra.JavaScript.eejs2py.install("users/dmlmont/spectral:spectral")        
    """
    if _check_if_module_exists(x):
        
        print(f"The module '{x}' is already installed!")
        
    else:
        
        ee_sources = _get_ee_sources_path()
        module_folder = os.path.join(ee_sources, x.split(":")[0])
        os.makedirs(module_folder)
        
        r = requests.get(_convert_path_to_ee_sources(x))
        
        open(_convert_path_to_ee_extra(x), 'wb').write(r.content)
        
        print(f"The module '{x}' was successfully installed!")


@Extra.add("JavaScript", "eejs2py", "evaluate")
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
    lists = re.findall(r'\[(.*?)\]',x)
    listsFull = []
    
    for l in lists:
        try:
            listsFull.append(list(map(float,l.split(","))))
        except:
            listsFull.append(l.replace('"',"").replace("'","").split(","))
            
    listsBrackets = {}
    counter = 0
    
    for i in lists:
        listsBrackets["eeExtraObject" + str(counter)] = "[" + i + "]"
        counter += 1
        
    for key, value in listsBrackets.items():
        x = x.replace(value,key)
        
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