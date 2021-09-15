"""JavaScript main module provide functions to transform  Eath Engine (EE) 
JavaScript code to Python code. The following functions are implemented:

I. Functions

* ee_js_to_py: Convert an EE JavaScript file to an EE Python file.
* ee_translate: Translate a EE Js module to a Python script.
* require:
"""

from ee_extra import translate
from ee_extra.JavaScript.merge import require


def ee_translate(x: str) -> str:
    """Translate a EE Js module to a Python script.

    Args:
        x (str): EE Js module as a string.

    Returns:
        str: EE Python script.
    """
    return translate(x)


def ee_js_to_py(in_file: str, out_file: str, black: bool = True) -> bool:
    """Convert an EE JavaScript file to an EE Python file.

    Args:
        in_file (str): File path of the input JavaScript.
        out_file (str): File path of the output Python script.

    Returns:
        bool: Return True if the conversion is successful.
    """

    with open(in_file, "r") as f_in:
        js_file = f_in.read()

    py_file = translate(js_file, black)

    with open(out_file, "w") as f_out:
        f_out.write(py_file)

    return True


def ee_require(x: str):
    """Requires a JavaScript module as a python module.

    Args:
        x (str): EE Js module as a string.

    Returns:
        module: Python module.
    """
    return require(x)