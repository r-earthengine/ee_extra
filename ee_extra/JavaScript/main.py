"""JavaScript main module provide functions to transform  Eath Engine (EE) 
JavaScript code to Python code. The following functions are implemented:

I. Functions

* ee_js_to_py: Convert an EE JavaScript file to an EE Python file.
* ee_translate: Translate a EE Js module to a Python script.
* require:
"""

from ee_extra import translate


def ee_translate(x: str) -> str:
    """Translate a EE Js module to a Python script.

    Args:
        x (str): EE Js module as a string.

    Returns:
        str: EE Python script.    
    """
    return translate(x)
    

def ee_js_to_py(in_file: str, out_file: str) -> bool:
    """Convert an EE JavaScript file to an EE Python file.

    Args:
        in_file (str): File path of the input JavaScript.
        out_file (str): File path of the output Python script.

    Returns:
        bool: Return True if the conversion is successful.
    """
    
    with open(in_file, 'r') as f_in:
        js_file = f_in.read()
    
    py_file = translate(js_file)
    
    with open(out_file, 'w') as f_out:
        f_out.write(py_file)
    
    return True

def require(x: str) -> str:
    pass    


if __name__ == "__main__":
    message = """
    function castCloudShadows(cloudMask, cloudHeights, sunAzimuth, sunZenith) {
    var cesaar = function(x) {
        var lesly = function(x) {
            return 1
        }
        var test=1
        return 1
    }    
    return cloudHeights.map(function (cloudHeight) {
        return projectCloudShadow(cloudMask, cloudHeight, sunAzimuth, sunZenith);            
    });
    }
    """
    ee_translate(message)