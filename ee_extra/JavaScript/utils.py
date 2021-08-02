"""Utils module store the auxiliary functions to translate JavaScript to Python."""

import regex
import random
import string
import re

def normalize_fn_style(x):
    """Normalize Javascript function style

    var xx = function(x){} --> function xx(x){}
    
    Args:
        x (str): [description]

    Returns:
        [str]: Python string
    """
    pattern = "var\s*(.*[^\s])\s*=\s*function"
    matches = re.finditer(pattern, x, re.MULTILINE)
    js_functions = list()
    for _, item in enumerate(matches):
        match = item.group(0)
        group = item.group(1)
        x = x.replace(match, f"function {group}")
    return x


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
    tail = "".join(tail_list)
    return base + tail


def indentify_js_functions(x):
    pattern = r"function\s*([\x00-\x7F][^\s]+)?\s*\((?:[^)(]+|\((?:[^)(]+|\([^)(]*\))*\))*\)\s*\{(?:[^}{]+|\{(?:[^}{]+|\{[^}{]*\})*\})*\}"
    matches = re.finditer(pattern, x, re.MULTILINE)
    js_functions = list()
    for _, item in enumerate(matches):
        js_functions.append(item.group())
        
    # It is a function with name?
    return js_functions


def from_js_to_py_fn1(js_function):
    """From Javascript to Python 1order

    Args:
        js_function (str): A Python string

    Returns:
        [dict]: Dictionary with py information
    """
    # 1. get function name
    pattern = r"function\s*([\x00-\x7F][^\s]+)\s*\(.*\)\s*{"
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
        "body": body,
        "fun_py_style": f"def {function_name}({args_name}):{body}\n",
        "anonymous": anonymous
    }
    
    return py_info    


def from_js_to_py_fn(js_function):
    """From Javascript to Python 1 or 2 order

    Args:
        js_function (str): A Python string

    Returns:
        [dict]: Dictionary with py information
    """    
    # It is a second order function?
    nreturns = re.findall(r"return\s", js_function)
    if len(nreturns) > 1:
        py_fn_result = from_js_to_py_fn1(js_function)
        fn_name = py_fn_result["fun_name"]
        fn_args = py_fn_result["args_name"]
        fpython_main = f"def {fn_name}({fn_args}):\n"
        
        # Get the body
        py_functions = from_js_to_py_fn1(py_fn_result["body"])
        
        # Particular cases
        ## Case #1
        # "return cloudHeights.map(function (cloudHeight) {\n return projectCloudShadow(cloudMask)})"            
        pattern = "function\s*([\x00-\x7F][^\s]+)?\s*\((?:[^)(]+|\((?:[^)(]+|\([^)(]*\))*\))*\)\s*\{(?:[^}{]+|\{(?:[^}{]+|\{[^}{]*\})*\})*\}"
        js_function = re.search(pattern, py_fn_result["body"])[0]
        x = x.replace(js_function, py_functions)

        
        
        return 
    else:
        return from_js_to_py_fn1(js_function)

def fix_identation(x):
    ident_base = "    "
    brace_counter = 0
    
    # remove multiple \n by just one
    pattern = r"\n+"
    x = re.sub(pattern, r"\n", x)

    x = regex.sub(r"\n\s+", "\n", x)

    # fix nested identation
    word_list = list()
    for word in x:
        if word in "{":
            brace_counter = brace_counter + 1
            word_list.append(word)
        elif word in "}":
            brace_counter = brace_counter - 1
            word_list.append(word)
        else:
            if word in "\n":
                word = "\n" + ident_base*(brace_counter + 1)
                word_list.append(word)
            else:
                word_list.append(word)
    x_fix = "".join(word_list)
            
    return x_fix

def add_identation(x):
    pattern = "\n"
    # identation in the body
    body_id = re.sub(pattern, r"\n    ", x)
    # identation in the header
    return "\n    " + body_id

def remove_identation_second_return(x):
    pattern = "    return "
    # split according to returns
    fn_groups = x.split(pattern)
    if len(fn_groups) != 3:
        raise ValueError("Invalid number of returns. Please open an issue in GH.")      
    return fn_groups[0] + pattern + fn_groups[1] + "return " + fn_groups[2]



def function_definition(x):
    # 1. Identify all the Javascript functions
    js_functions = indentify_js_functions(x)
    for js_function in js_functions:    
        nreturns = re.findall(r"return\s", js_function)        
        # 2. if a nested function?
        if len(nreturns) > 1:
            # 3. From js function by Python function (1 order)
            py_function = from_js_to_py_fn1(js_function)
            f_name = py_function["fun_name"]
            f_args = py_function["args_name"]
            header = f"def {f_name}({f_args}):\n    "
            
            # 4. From js function by Python function (2 order)
            py_body = fix_identation(py_function["body"])
            second_group = function_definition(py_body)
            second_group = add_identation(second_group)
            
            # Special Case #1
            # remove extra space in return
            # \ndef FZEgLgBAUzt7Sg6(cloudHeight):\n    return projectCloudShadow(cloudMask);\n    \n\n    return cloudHeights.map(FZEgLgBAUzt7Sg6);\n    
            nreturns = re.findall(r"return\s", js_function)
            if len(nreturns) > 1:
                second_group = remove_identation_second_return(second_group)
                
            x = x.replace(js_function, header + second_group)
        else:
            # 3. Remove Javascript function by Python function
            py_function = from_js_to_py_fn1(js_function)
            py_function_f = fix_identation(py_function["fun_py_style"])
            if py_function["anonymous"]:
                x = x.replace(js_function, py_function["fun_name"])                                
                x = "\n" + py_function_f + "\n" + x
            else:
                x = x.replace(js_function, "\n" + py_function_f)
    return x


# 7. Change "{x = 1}" by "{'x' = 1}".
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
    
    x = normalize_fn_style(x)
    x = variable_definition(x)
    x = logical_operators_boolean_null_comments(x)
    x = multiline_comments(x)
    x = multiline_method_chain(x)
    x = function_definition(x)       
    x = dictionary_keys(x)
    x = dictionary_object_access(x)
    x = keyword_arguments_object(x)    
    x = if_statement(x)
    x = array_isArray(x)
    x = for_loop(x)
        
    return x

if __name__ == "__main__":
    msg = """ 
    function projectCloudShadow(cloudMask, cloudHeight, φ, θ) {
        cloudHeight = ee.Number(cloudHeight);
        // convert to radians
        var π = Math.PI;
        θ = ee.Number(0.5).multiply(π).subtract(ee.Number(θ).multiply(π).divide(180.0));
        φ = ee.Number(φ).multiply(π).divide(180.0).add(ee.Number(0.5).multiply(π));
        // compute shadow offset (vector length)
        var offset = θ.tan().multiply(cloudHeight);
        // compute x, y components of the vector
        var proj = cloudMask.projection();
        var nominalScale = proj.nominalScale();
        var x = φ.cos().multiply(offset).divide(nominalScale).round();
        var y = φ.sin().multiply(offset).divide(nominalScale).round();
        return cloudMask.changeProj(proj, proj.translate(x, y)).set('height', cloudHeight)
    }
    function castCloudShadows(cloudMask, cloudHeights, sunAzimuth, sunZenith) {
        return cloudHeights.map(function (cloudHeight) {
            return projectCloudShadow(cloudMask, cloudHeight, sunAzimuth, sunZenith);
        });
    }

    function lesly(b) { 
        var cesar = 1;
        
        for (let i = 0; i < 9; i++) {
            str = str + i;
        }
        
        return false        
    }
    function computeCloudShadowMask(sunElevation, sunAzimuth, cloudMask, options) {
        var maxCloudHeight = 8000 // in image pixel units
        var cloudHeightStep = 200
        var radiusDilate = 10
        var radiusErode = 3
        
        if(options) {
            maxCloudHeight = options.maxCloudHeight || maxCloudHeight
            cloudHeightStep = options.cloudHeightStep || cloudHeightStep
            radiusDilate = options.radiusDilate || radiusDilate
            radiusErode = options.radiusErode || radiusErode
        }
        
        // generate cloud heights
        var cloudHeights = ee.List.sequence(100, maxCloudHeight, cloudHeightStep);
        
        // cast cloud shadows
        var cloudShadowMask = ee.ImageCollection(castCloudShadows(cloudMask, cloudHeights, sunAzimuth, sunElevation)).max();
        
        // remove clouds
        cloudShadowMask = cloudShadowMask.updateMask(cloudMask.not());
        return cloudShadowMask;
    }
    exports.computeCloudShadowMask = computeCloudShadowMask
    """
    with open("test3.py", "w") as file:
        file.write(translate(msg))
    print("Done!")
