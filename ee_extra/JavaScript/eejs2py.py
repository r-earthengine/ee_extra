"""JavaScript module provide functions to transform 
Eath Engine (EE) JavaScript code to Python code. The following
functions are implemented:

I. Functions

* _convert_path_to_ee_sources: Get the remote module path from the 'ee-sources' GCS bucket.
* _get_ee_sources_path: Get the local module path.
* _convert_path_to_ee_extra: Convert remote module path to local module path.
* _check_if_module_exists: Check if a EE local module exists.
* _open_module_as_str: Open a EE local module as a string.
* _get_dependencies: Get the dependencies of an EE complex module.
* _install: Install an specific EE Js file in their system.
* install: Install an specific EE Js module in their system.
* uninstall: Install an specific EE Js module.
* translate: Translate a EE Js module to a Python script.
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
    """Get the remote module path from the 'ee-sources' GCS bucket.

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


def translate(x: str) -> str:
    """Translates a JavaScript script to a Python script.

    Args:
        x : A JavaScript script.

    Returns:
        A Python script.

    Examples:
        >>> import ee
        >>> from ee_extra.JavaScript.eejs2py import translate
        >>> ee.Initialize()
        >>> translate("var x = ee.ImageCollection('COPERNICUS/S2_SR')")
    """

    # 1. Remove curly braces
    # For example: "obj={'b':'a'}}" --> "obj={'b':'a'}"
    def delete_brackets(x):
        counter = 0
        newstring = ""
        for char in x:
            if char == "{":
                counter += 1
            elif char == "}":
                counter -= 1
            if counter >= 0:
                newstring += char
            else:
                counter = 0
        return newstring

    
    # 2. Remove reserved keyword "var"
    # For example: "var x = 1" --> "x = 1"
    def variable_definition(x):
        pattern = r"var(.*?)="
        matches = re.findall(pattern, x, re.DOTALL)
        if len(matches) > 0:
            for match in matches:
                x = x.replace(f"var{match}=", f"{match.replace(' ','')} =")
        return x

    # 3. Change logical operators, boolean, null and comments
    # For example: "m = s.and(that);" -> "m = s.And(that)"
    def logical_operators_boolean_null_comments(x):
        reserved = {
            ".and": ".And",
            ".or": ".Or",
            ".not": ".Not",
            "true": "True",
            "false": "False",
            "null": "None",
            "//": "#",
            "!": " not ",
        }
        for key, item in reserved.items():
            x = x.replace(key, item)
        return x

    # 4. /* . . . */ : Replace "/*" by "#".
    def multiline_comments(x):
        pattern = r"/\*(.*?)\*/"
        matches = re.findall(pattern, x, re.DOTALL)
        if len(matches) > 0:
            for match in matches:
                x = x.replace(match, match.replace("\n", "\n#"))
        x = x.replace("/*", "#")
        return x
    
    # 5. /* ... */: Add "#" to each line of the multiline comment block.
    def multiline_method_chain(x):
        lines = x.split("\n")
        for i in range(len(lines)):
            if lines[i].replace(" ", "").startswith("."):
                lines[i - 1] = lines[i - 1] + " \\"
        return "\n".join(lines)

    # 6. Replace Js function style to Python function style.
    # For example: "var f = function(x){" or "function f(x){" by "def f(x):"        
    def random_fn_name():
        # body (7)
        body_list = list()
        for x in range(9):
            body_list.append(random.choice(string.ascii_letters))
        base = "".join(body_list)
    
        # number (4)
        tail_list = list()
        for x in range(6):
            tail_list.append(random.choice(string.ascii_letters+"123456789"))    
    return base+tail


    def indentify_js_functions(x):
        pattern = r"^(?:[\s]+)?(?:var|)?(?:[\x00-\x7F.][^\s]+(?:\.)?)?(?:\s)?(?:[\x00-\x7F][^\s]+\s?=)?\s?(?:[\x00-\x7F][^\s]+\s+\:\s+)?(?:function\s?)?(?:[\x00-\x7F][^\s]+)?\s?\(.*\)\s?(?:.+)?([=>]:)?\{(?:(?:[^}{]+|\{(?:[^}{]+|\{[^}{]*\})*\})*\}(?:\s?\(.*\)\s?\)\s?)?)?(?:\;)?"
        matches = re.finditer(pattern, x, re.MULTILINE)

        js_functions = list()
        for _, item in enumerate(matches):
            js_functions.append(item.group())
            
        # It is a function with name?
        return js_functions

    def from_js_to_py_fn(js_function):
        # 1. get function name
        pattern = r"var\s*([\x00-\x7F][^\s]+)\s*=\s*function|function\s*([\x00-\x7F][^\s]+)\s*\(.*\)\s*{"
        regex_result = re.findall(pattern, js_function)
        
        # if it is a anonymous function
        if len(regex_result) == 0:
            anonymous = True
            function_name = random_fn_name()
        else:
            anonymous = False
            function_name = "".join(regex_result[0])
        
        # 2. get args
        pattern = r"function\s*[\x00-\x7F][^\s]*\s*\(\s*([^)]+?)\s*\)\s*{|function\(\s*([^)]+?)\s*\)\s*"
        args_name = "".join(re.findall(pattern, js_function)[0])
        
        # 3. get body
        pattern = r"({(?>[^{}]+|(?R))*})"
        body = regex.search(pattern, js_function)[0][1:-1]
        if not body[0] == "\n":
        body = "\n    " + body
        
        # 3. py function info
        py_info = {
            'fun_name': function_name,
            "args_name": args_name, 
            "fun_py_style": f"def {function_name}({args_name}):{body}\n",
            "anonymous": anonymous
        }
        
        return py_info


    def function_definition(x):
        # 1. Identify all the Javascript functions
        js_functions = indentify_js_functions(x)
        
        # 2. Python function list
        py_functions_list = list()
        #js_function = js_functions[5]
        
        for js_function in js_functions:
            
            # 3. Remove Javascript function by Python function
            py_function = from_js_to_py_fn(js_function)
            
            if py_function["anonymous"]:
                x = x.replace(js_function, py_function["fun_name"])
                x = "\n" + py_function["fun_py_style"] + "\n" + x
            else:
                x = x.replace(js_function, "\n" + py_function["fun_py_style"])            
        return x


    # # 7. Change "{x = 1}" by "{'x' = 1}".
    def dictionary_keys(x):
        pattern = r"{(.*?)}"
        dicts = re.findall(pattern, x, re.DOTALL)
        if len(dicts) > 0:
            for dic in dicts:
                items = dic.split(",")
                for item in items:
                    pattern = r"(.*):(.*)"
                    item = re.findall(pattern, item)
                    if len(item) > 0:
                        for i in item:
                            i = list(i)
                            j = i[0].replace('"', "").replace("'", "").replace(" ", "")
                            x = x.replace(f"{i[0]}:{i[1]}", f"'{j}':{i[1]}")
        return x

    # NECESITA REVISION
    # Debe cambiar el acceso a los diccionarios. Es capaz de cambiar "exports.x = 1" por "exports['x'] = 1"
    # Pero cuando hay otros puntos en el texto tambien los cambia, como "https://google.com" por "https://google['com']"
    # Esto es un error.
    def dictionary_object_access(x):
        pattern = r"\.(.*)"
        matches = re.findall(pattern, x)
        if len(matches) > 0:
            for match in matches:
                if "=" in match:
                    splitted = match.split("=")
                    key = splitted[0].replace(" ", "")
                    x = x.replace(f".{match}", f"['{key}'] ={splitted[1]}")
                elif (
                    "(" not in match
                    and ")" not in match
                    and len(match) > 0
                    and not any(char.isdigit() for char in match)
                ):
                    x = x.replace(f".{match}", f"['{match}']")
        return x

    # FUNCIONA
    # Cambia "f({x = 1})" por "f(**{x = 1})"
    def keyword_arguments_object(x):
        pattern = r"\((.*){(.*)}(.*)\)"
        matches = re.findall(pattern, x, re.DOTALL)
        if len(matches) > 0:
            for match in matches:
                match = list(match)
                x = x.replace("{" + match[1] + "}", "**{" + match[1] + "}")
        return x

    # NECESITA REVISION
    # Debe cambiar "ee.ImageCollection(x).map(function(x) { return x })" por "ee.ImageCollection(x).map(lambda x: x)"
    # pero se que no esta completo
    def anonymous_function_mapping(x):
        pattern = r"\.map\((.*)function\((.*)\)"
        matches = re.findall(pattern, x)
        if len(matches) > 0:
            for match in matches:
                match = list(match)
                x = x.replace(f".map(function({match[1]})", f".map(lambda {match[1]}:")
        return x

    # FUNCIONA
    # Cambia "if(x){" por "if x:"
    def if_statement(x):
        pattern = r"if(.*?)\((.*)\)(.*){"
        matches = re.findall(pattern, x)
        if len(matches) > 0:
            for match in matches:
                match = list(match)
                x = x.replace(
                    "if" + match[0] + "(" + match[1] + ")" + match[2] + "{", f"if {match[1]}:"
                )
        return delete_brackets(x)

    # FUNCIONA
    # Cambia "Array.isArray(x)" por "isinstance(x,list)"
    def array_isArray(x):
        pattern = r"Array\.isArray\((.*?)\)"
        matches = re.findall(pattern, x)
        if len(matches) > 0:
            for match in matches:
                x = x.replace(f"Array.isArray({match})", f"isinstance({match},list)")
        return x

    # FUNCIONA
    # Cambia "for(var i = 0;i < x.length;i++){" por "for i in range(0,len(x),1):"
    def for_loop(x):
        pattern = r"for(.*)\((.*);(.*);(.*)\)(.*){"
        matches = re.findall(pattern, x)
        if len(matches) > 0:
            for match in matches:
                match = list(match)
                # Get the start value and the iter name
                i = match[1].replace("var ", "")
                i = i.replace(" ", "").split("=")
                start = i[1]
                i = i[0]
                # Get the end/stop value
                end = (
                    match[2]
                    .replace("=", " ")
                    .replace(">", " ")
                    .replace("<", " ")
                    .replace("  ", " ")
                    .split(" ")[-1]
                )
                if "." in end:
                    end = end.split(".")[0]
                    end = f"len({end})"
                # Get the step value
                if "++" in match[3]:
                    step = 1
                elif "--" in match[3]:
                    step = -1
                elif "+=" in match[3]:
                    step = match[3].replace(" ", "").split("+=")[-1]
                elif "-=" in match[3]:
                    step = match[3].replace(" ", "").split("+=")[-1]
                    step = f"-{step}"
                x = x.replace(
                    "for"
                    + match[0]
                    + "("
                    + match[1]
                    + ";"
                    + match[2]
                    + ";"
                    + match[3]
                    + ")"
                    + match[4]
                    + "{",
                    f"for {i} in range({start},{end},{step}):",
                )
        x = x.replace(";", "")
        return delete_brackets(x)

    x = variable_definition(x)
    x = logical_operators_boolean_null_comments(x)
    x = multiline_comments(x)
    x = multiline_method_chain(x)
    x = function_definition(x)
    x = dictionary_keys(x)
    x = dictionary_object_access(x)
    x = keyword_arguments_object(x)
    x = anonymous_function_mapping(x)
    x = if_statement(x)
    x = array_isArray(x)
    x = for_loop(x)

    return x


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
