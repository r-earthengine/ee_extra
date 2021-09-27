"""Auxiliary module store functions to translate JavaScript to Python."""

import random
import re
import string
from operator import add

import regex
from black import FileMode, format_str


# 1. Normalize function name
# For example: "var exp = function(x){ }" --> "function exp(x) { }"
def normalize_fn_style(x: str) -> str:
    """Normalize Javascript function style

    var xx = function(x){} --> function xx(x){}

    Args:
        x (str): A Js script as string.

    Returns:
        [str]: Python string
    """
    pattern = "var\s*(.*[^\s])\s*=\s*function"
    matches = re.finditer(pattern, x, re.MULTILINE)
    for _, item in enumerate(matches):
        match = item.group(0)
        group = item.group(1)
        x = x.replace(match, f"function {group}")
    return x


# 2. Remove curly braces
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


# 3. Remove reserved keyword "var"
# For example: "var x = 1" --> "x = 1"
def variable_definition(x):
    pattern = r"var(.*?)="
    matches = re.findall(pattern, x, re.DOTALL)
    if len(matches) > 0:
        for match in matches:
            x = x.replace(f"var{match}=", f"{match.replace(' ','')} =")
    return x


# 4. Change logical operators, boolean, null and comments
# For example: "m = s.and(that);" -> "m = s.And(that)"
def logical_operators_boolean_null_comments(x):
    reserved = {
        "\.and\(": ".And(",
        "\.or\(": ".Or(",
        "\.not\(": ".Not(",
        "(?<![a-zA-Z])true(?![a-zA-Z])": "True",
        "(?<![a-zA-Z])false(?![a-zA-Z])": "False",
        "(?<![a-zA-Z])null(?![a-zA-Z])": "None",
        "//": "#",
        "!": " not ",
        "\|\|": " or ",
        "===": " == ",
    }

    for key, item in reserved.items():
        x = regex.sub(key, item, x)
        # x = x.replace(key, item)
    # Correct https://
    x = x.replace("https:#", "https://")
    x = x.replace("http:#", "http://")
    return x


# 5. /* . . . */ : Replace "/*" by "#".
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
            j = 1
            while lines[i - j].replace(" ", "").startswith("#"):
                j = j + 1
            lines[i - j] = lines[i - j] + " \\"
    return "\n".join(lines)


# 7. Random name generator
def random_fn_name():
    """Generate a random name"""
    # body (7)
    body_list = list()
    for x in range(9):
        body_list.append(random.choice(string.ascii_letters))
    base = "".join(body_list)

    # number (4)
    tail_list = list()
    for x in range(8):
        tail_list.append(random.choice(string.ascii_letters + "123456789"))
    tail = "".join(tail_list)
    return base + tail


# 8. Identify all the functions
def indentify_js_functions(x: str) -> list:
    """Identify all the functions in a Javascript file

    Args:
        x (str): A Js script as string.

    Returns:
        [list]: A list with all the functions names.
    """
    pattern = r"function\s*([A-z0-9]+)?\s*\((?:[^)(]+|\((?:[^)(]+|\([^)(]*\))*\))*\)\s*\{(?:[^}{]+|\{(?:[^}{]+|\{[^}{]*\})*\})*\}"

    matches = re.finditer(pattern, x, re.MULTILINE)
    js_functions = list()
    for _, item in enumerate(matches):
        js_functions.append(item.group())

    # It is a function with name?
    return js_functions


# 9. Convert simple JavaScript functions to Python
def from_js_to_py_fn_simple(js_function):
    """From Javascript to Python 1order
    js_function
    Args:
        js_function (str): A Python string

    Returns:
        [dict]: Dictionary with py information
    """
    # Get function header
    heard_func = list()
    for word in js_function:
        if word == "{":
            heard_func.append("{")
            break
        elif word == "\n":
            continue
        else:
            heard_func.append(word)

    fn_header = "".join(heard_func)

    # 1. get function name
    pattern = r"function\s*([\x00-\x7F][^\s]+)\s*\(.*\)\s*{"
    regex_result = re.findall(pattern, fn_header)

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
        "fun_name": function_name,
        "args_name": args_name,
        "body": body,
        "fun_py_style": f"def {function_name}({args_name}):{body}\n",
        "anonymous": anonymous,
    }
    return py_info


def fix_identation(x):
    """Fix identation of a Python script"""
    ident_base = "    "
    brace_counter = 0

    # if first element of the string is \n remove!
    if x[0] == "\n":
        x = x[1:]

    # remove multiple \n by just one
    pattern = r"\n+"
    x = re.sub(pattern, r"\n", x)

    # Detect the spaces of the first identation
    x = regex.sub(r"\n\s+", "\n", x)

    # fix nested identation
    brace_counter = 0
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
                word = "\n" + ident_base * (brace_counter)
                word_list.append(word)
            else:
                word_list.append(word)
    x_fix = "".join(word_list)

    return x_fix


def add_identation(x):
    """Add extra identation in a Python function body"""
    pattern = "\n"
    # identation in the body
    body_id = re.sub(pattern, r"\n    ", x)
    # identation in the header
    return "\n    " + body_id


def check_nested_fn_complexity(x):
    """Thi is useful to avoid errors related to catastrophic backtracking"""
    pattern = "\s{16}function"
    if re.search(pattern, x):
        raise ValueError("This module does not support 4-level nested functions.")
    return False


def remove_extra_spaces(x):
    """Remove \n and \s if they are at the begining of the string"""
    if x[0] == "\n":
        # Remove spaces at the beginning
        word_list = list()
        forward_counter = 0
        for word in x:
            if (word == "\n" or word.isspace()) and forward_counter == 0:
                pass
            else:
                forward_counter = -1
                word_list.append(word)

        # Remove spaces at the end
        back_counter = 0
        while back_counter <= 0:
            counter = back_counter - 1
            if word_list[counter] == " ":
                del word_list[counter]
            else:
                back_counter = 1
        return "".join(word_list)
    return x


## exports.addBand = function(landsat){ var wrap = function(image){ return 0;} return 0;}
def remove_assignment_specialcase_01(x):
    # does anonymous function asignation exists?
    pattern01 = r"[exports|eeExtraExports].*=.*function.*\("
    exports_lines = re.findall(pattern01, x)

    if len(exports_lines) > 0:
        for exports_line in exports_lines:
            export_str = re.findall("([exports|eeExtraExports].*)=", exports_line)[0]
            rname = random_fn_name()
            pattern02 = export_str + "=.*function"
            x = re.sub(pattern02, ("function " + rname), x)

            # add export at the end of the file
            x = x + "\n" + export_str + " = " + rname
    return x


def function_definition(x):

    # Special case #01:
    # export.css = function(landsat){ var wrap = function(image){ return 0;} return 0;}
    x = remove_assignment_specialcase_01(x)

    # Check nested functionn complexity
    check_nested_fn_complexity(x)

    # 1. Identify all the Javascript functions
    js_functions = indentify_js_functions(x)

    # js_function = js_functions[0]

    for js_function in js_functions:
        nreturns = re.findall(r"return\s", js_function)
        # 2. if a nested function?
        if len(nreturns) > 1:
            # 3. From js function by Python function (1 order)
            py_function = from_js_to_py_fn_simple(js_function)
            f_name = py_function["fun_name"]
            f_args = py_function["args_name"]
            header = f"def {f_name}({f_args}):\n    "

            # 4. From js function by Python function (2 order)
            new_body = remove_extra_spaces(py_function["body"])
            py_body = fix_identation(new_body)
            second_group = function_definition(py_body)
            second_group = add_identation(second_group)

            x = x.replace(js_function, header + second_group)
        else:
            # 3. Remove Javascript function by Python function
            py_function = from_js_to_py_fn_simple(js_function)
            py_function_f = py_function["fun_py_style"]
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
                pattern = r"(.*?):(.*)"
                item = re.findall(pattern, item)
                if len(item) > 0:
                    for i in item:
                        i = list(i)
                        j = i[0].replace('"', "").replace("'", "").replace(" ", "")
                        x = x.replace(f"{i[0]}:{i[1]}", f"'{j}':{i[1]}")
    return x


def is_float(x):
    """Is a string a float?. Return a bool."""
    try:
        float(x)
        return True
    except ValueError:
        return False


def dict_replace(x, match, word, new_word):
    """Replace name.name only if they are not inside quotation marks"""

    def inside_quoation_marks(x, word):
        pattern = r"([\"'])(?:(?=(\\?))\2.)*?\1"
        if re.search(pattern, x):
            qm_word = re.search(pattern, x).group(0)
            return word in qm_word
        else:
            return False

    if inside_quoation_marks(match, word):
        return x
    else:
        return x.replace(word, new_word)


def dictionary_object_access(x):
    """Replace <name01>.<name02> only when name01 is a dictionary"""

    # Search in all lines .. it matchs <name>.<name>
    pattern = r"^(?=.*[\x00-\x7F][^\s]+\.[\x00-\x7F][^\s]+)(?!.*http).*$"
    matches = re.findall(pattern, x, re.MULTILINE)

    # match = matches[0]
    for match in matches:
        if len(match) > 0:
            if match[0] == "#":
                continue

        # Search in one line.
        pattern1 = (
            r"[A-Za-z0-9Α-Ωα-ωίϊΐόάέύϋΰήώ\[\]_]+\.[A-Za-z0-9Α-Ωα-ωίϊΐόάέύϋΰήώ\[\]_]+"
        )
        pattern2 = pattern1 + "."

        # <name>.<name> dicts take a decision based on the next letter but when
        # the next letter is a \n it cause problems. When this happens we add a ')'
        matches_at_line1 = re.findall(pattern1, match)
        matches_at_line2 = re.findall(pattern2, match)

        matches_at_line = list()
        for _, y in zip(matches_at_line1, matches_at_line2):
            if _ == y:
                matches_at_line.append(y + ")")
            else:
                matches_at_line.append(y)

        # match_line = matches_at_line[0]
        for match_line in matches_at_line:
            # If is a number pass
            if is_float(match_line[:-1]):
                continue

            # If is a method or a function
            if ("(" in match_line[-1]) or ("ee." in match_line[:-1]):
                continue

            # If is a math
            if "Math." in match_line:
                new_word = match_line.lower()
                x = dict_replace(x, match, match_line, new_word)
            else:
                nlist = match_line[:-1].split(".")
                arg_nospace = re.sub(r"\s", "", nlist[1])
                new_word = '%s["%s"]' % (nlist[0], arg_nospace)
                x = dict_replace(x, match, match_line[:-1], new_word)
    return x


# Change "f({x = 1})" por "f(**{x = 1})"
def keyword_arguments_object(x):
    pattern = r"\({(.*?)}\)"
    matches = re.findall(pattern, x, re.DOTALL)
    if len(matches) > 0:
        for match in matches:
            x = x.replace("{" + match + "}", "**{" + match + "}")
    pattern = r"ee\.Dictionary\(\*\*{"
    matches = re.findall(pattern, x, re.DOTALL)
    if len(matches) > 0:
        for match in matches:
            x = x.replace(match, "ee.Dictionary({")
    return x


# Change "if(x){" por "if x:"
def if_statement(x):
    pattern = r"}(.*?)else(.*?)if(.*?){"
    matches = re.findall(pattern, x)
    if len(matches) > 0:
        for match in matches:
            match = list(match)
            x = x.replace(
                "}" + match[0] + "else" + match[1] + "if" + match[2] + "{",
                f"elif {match[2]}:",
            )
    pattern = r"if(.*?)\((.*)\)(.*){"
    matches = re.findall(pattern, x)
    if len(matches) > 0:
        for match in matches:
            match = list(match)
            x = x.replace(
                "if" + match[0] + "(" + match[1] + ")" + match[2] + "{",
                f"if {match[1]}:",
            )
    pattern = r"}(.*?)else(.*?){"
    matches = re.findall(pattern, x)
    if len(matches) > 0:
        for match in matches:
            match = list(match)
            x = x.replace("}" + match[0] + "else" + match[1] + "{", "else:")
    return delete_brackets(x)


# Change "Array.isArray(x)" por "isinstance(x,list)"
def array_isArray(x):
    pattern = r"Array\.isArray\((.*?)\)"
    matches = re.findall(pattern, x)
    if len(matches) > 0:
        for match in matches:
            x = x.replace(f"Array.isArray({match})", f"isinstance({match},list)")
    return x


# Change "for(var i = 0;i < x.length;i++){" por "for i in range(0,len(x),1):"
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


def add_packages(x):
    """add ee and math packages to the code. AttrDict is used by default."""
    py_packages = "import ee\nimport math\n"
    user_dict = (
        "\nclass AttrDict(dict):\n    def __init__(self, *args, **kwargs):\n        super(AttrDict, self)"
        + ".__init__(*args, **kwargs)\n        self.__dict__ = self\n"
    )
    exports_dict = "\nexports = AttrDict()\n"
    return py_packages + user_dict + exports_dict + x


# If a line ends with equal merge it with the new line
def ends_with_equal(x):
    # get True is "=" is the last character
    last_is_plus = lambda x: x[-1] == "="
    
    # Remove all whitespace at the end.
    lines = [regex.sub(r'\s+S*$', '', line) for line in x.split("\n")]
    
    # Get "1" is the last chr is "=" otherwise get "0"
    is_last_chr_plus = list()
    for line in lines:
        if len(line) > 0:
            cond = str(int(last_is_plus(line)))
        else:
            cond = "0"
        is_last_chr_plus.append(cond)
    subgroups = "".join(is_last_chr_plus) # e.g. "011000100"
    
    # If no "=", then return the original string
    if int(subgroups) == 0:
        return x
    
    # Create subgroups
    # Some lines finish with "+" identiy those lines and create subgroups.
    save_breaks_01 = []
    save_breaks_02 = []
    for index in range(0, len(subgroups) - 1):
        if subgroups[index] == "1" and subgroups[index-1] == "0":
            save_breaks_01.append(index)
        if subgroups[index] == "1" and subgroups[index+1] == "0":
            save_breaks_02.append(index)
    final_subgroups = [
        list(range(save_breaks_01[index], save_breaks_02[index] + 2)) 
        for index in range(len(save_breaks_01))
    ]  # e.g. [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
    
    # Identify the lines that not end in"+" 
    # Identify the lines that not end in"+" 
    flat_final_groups = sum(final_subgroups, [])
    no_plus_lines = [
        index for index in range(len(lines)) if not index in flat_final_groups
    ]

    no_plus_lines.insert(0, - 1) # add negative threshold
    no_plus_lines.insert(len(lines), len(lines) + 100) # add positive threshold
    
    # Merge no_plus_lines and final_subgroups
    position_to_add_subgroups = [
        index
        for index in range(len(no_plus_lines) - 1)
        if (no_plus_lines[index] + 1) != no_plus_lines[index+1] 
    ]
    norm_v = list(range(1, len(position_to_add_subgroups)+ 1))
    position_to_add_subgroups = list(map(add, position_to_add_subgroups, norm_v))

    for index in range(len(final_subgroups)):
        no_plus_lines.insert(position_to_add_subgroups[index], final_subgroups[index])
    no_plus_lines.pop(0)
    no_plus_lines.pop(-1)
    
    # Create the new x string
    final_x = list()
    for index in no_plus_lines:
        if isinstance(index, list):
            final_x.append("".join([lines[index2] for index2 in index]))
        else:
            final_x.append(lines[index])
    return "\n".join(final_x)

# If a line from file ends in a "+", merge with the next line.
def ends_with_plus(x):
    # get True is "+" is the last character
    last_is_plus = lambda x: x[-1] == "+"
    
    # Remove all whitespace at the end.
    lines = [regex.sub(r'\s+S*$', '', line) for line in x.split("\n")]
    
    # Get "1" is the last chr is "+" otherwise get "0"
    is_last_chr_plus = list()
    for line in lines:
        if len(line) > 0:
            cond = str(int(last_is_plus(line)))
        else:
            cond = "0"
        is_last_chr_plus.append(cond)
    subgroups = "".join(is_last_chr_plus) # e.g. "011000100"
    
    # If no "+", then return the original string
    if int(subgroups) == 0:
        return x
    
    # Create subgroups
    # Some lines finish with "+" identiy those lines and create subgroups.
    save_breaks_01 = []
    save_breaks_02 = []
    for index in range(0, len(subgroups) - 1):
        if subgroups[index] == "1" and subgroups[index-1] == "0":
            save_breaks_01.append(index)
        if subgroups[index] == "1" and subgroups[index+1] == "0":
            save_breaks_02.append(index)
    final_subgroups = [
        list(range(save_breaks_01[index], save_breaks_02[index] + 2)) 
        for index in range(len(save_breaks_01))
    ]  # e.g. [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
    
    # Identify the lines that not end in"+" 
    flat_final_groups = sum(final_subgroups, [])
    no_plus_lines = [
        index for index in range(len(lines)) if not index in flat_final_groups
    ]
    no_plus_lines.insert(0, - 1) # add negative threshold
    no_plus_lines.insert(len(lines), len(lines) + 100) # add positive threshold
    
    # Merge no_plus_lines and final_subgroups
    position_to_add_subgroups = [
        index
        for index in range(len(no_plus_lines) - 1)
        if (no_plus_lines[index] + 1) != no_plus_lines[index+1] 
    ]
    norm_v = list(range(1, len(position_to_add_subgroups)+ 1))
    position_to_add_subgroups = list(map(add, position_to_add_subgroups, norm_v))

    for index in range(len(final_subgroups)):
        no_plus_lines.insert(position_to_add_subgroups[index], final_subgroups[index])
    no_plus_lines.pop(0)
    no_plus_lines.pop(-1)
    
    # Create the new x string
    final_x = list()
    for index in no_plus_lines:
        if isinstance(index, list):
            final_x.append("".join([lines[index2] for index2 in index]))
        else:
            final_x.append(lines[index])
    return "\n".join(final_x)

def translate(x: str, black: bool = True) -> str:
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
    x = for_loop(x)
    x = function_definition(x)
    x = dictionary_keys(x)
    x = dictionary_object_access(x)
    x = keyword_arguments_object(x)
    x = if_statement(x)
    x = array_isArray(x)
    x = add_packages(x)
    x = ends_with_plus(x)
    x = ends_with_equal(x)
    
    if black:
        x = format_str(x, mode=FileMode())

    return x