"""
Auxiliary module with functions to translate JavaScript functions to Python.

In JavaScript there is three diferent ways of GEE users define functions:

    1. GEE users define the function at the beginning of the line (we love u!).
        function name(args) {          |    var name = function(args) {
            return x;                  |         return x;
        }                              |    };
    2. GEE users define the function in the middle of the line (yeah it's ok).
        ic.map(function(x) {return x})
    
    3. GEE users define function after export (we hate u!).
        exports.addBand = function(landsat){ var wrap = function(image){ return 0;} return 0;}        

This module try to convert all theses cases to Python. If you consider that
there is more cases that must be added to the module, please, contact us by
GitHub :).
"""

import random
import string

import regex

from ee_extra.JavaScript.translate_general import from_bin_to_list


def random_fn_name():
    """Name generator.

    Returns:
        [str]: A random name generator of 17 character.
    Examples:
        >>> from ee_extra import random_fn_name
        >>> random_fn_name()
        >>> # VMpzftMJpjuk8Etv9
    """
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


def is_nested_list(mlist):
    """Is a list nested?

    Args:
        l ([list]): A Python list.

    Returns:
        [bool]: 1 is is a nested list, 0 is not and -1 is not a list.

    Examples:
        >>> from ee_extra import is_nested_list
        >>> is_nested_list([1,2,3])
        >>> # 0
        >>> is_nested_list([1,[2],3])
        >>> # 1
        >>> is_nested_list("Lesly")
        >>> # -1
    """
    if not isinstance(mlist, list):
        return -1  # is not a list
    if not any([isinstance(line, list) for line in mlist]):
        return 0  # if a list but not nested
    else:
        return 1  # if a nested list


# --------------------------------------------------------------------------
# First Case ---------------------------------------------------------------
# --------------------------------------------------------------------------
# Remember that previously we run 'normalize_fn_name' to make uniform Js function
# definition style (var fun = function(bla, bla) -> function fun(bla, bla)).
def from_js_to_py_fn_simple(js_function):
    """From Javascript no-nested Case1 function to Python.
    Args:
        js_function (str): A Python string
    Returns:
        [dict]: Dictionary with the following keys:
                    - fun_name: function name
                    - args_name: list of arguments names
                    - body: function body
                    - fun_py_style: function in Python.
                    - anonymous: True if the function is anonymous, 0 if not.
    Examples:
        >>> from ee_extra import from_js_to_py_fn_simple
        >>> js_function = "function(x) { return x}"
        >>> from_js_to_py_fn_simple(js_function)["fun_py_style"]
        >>> # def pUsmYqrpCbaOKduJA(x):\n    return x\n
    """
    # 1. Get function header
    if isinstance(js_function, list):
        fn_header = "\n".join(js_function)
    else:
        fn_header = js_function

    # is there a assignement? e.g. eeExtraExports0.addBand = function(image) {...}
    tentative_name = regex.findall("(.*\..*)\s=\sfunction\(", fn_header)

    # 2. get function name
    pattern = r"function\s*([\x00-\x7F][^\s]+)\s*\(.*\)\s*{"
    regex_result = regex.findall(pattern, fn_header)

    # 3. if it is a anonymous function assign a random name
    if len(regex_result) == 0:
        anonymous = True
        function_name = random_fn_name()
    else:
        anonymous = False
        function_name = "".join(regex_result[0])

    # 4. get args
    pattern = r"function\s*[\x00-\x7F][^\s]*\s*\(\s*([^)]+?)\s*\)\s*{|function\(\s*([^)]+?)\s*\)\s*"
    int_args = regex.findall(pattern, fn_header)
    if int_args == []:
        args_name = ""
    else:
        args_name = "".join(int_args[0])
        new_args = list()
        for arg in args_name.split(","):
            if "=" not in arg:
                new_args.append(arg.strip() + "='__None'")
            else:
                new_args.append(arg.strip())
        args_name = ", ".join(new_args)

    # 5. get body
    pattern = r"({(?>[^{}]+|(?R))*})"
    body = regex.search(pattern, fn_header)[0][1:-1].rstrip()

    # 6. Init space
    init_space = regex.match("\s*", fn_header)[0]

    # 7. py function info
    if tentative_name == []:
        fun_py_style = f"{init_space}def {function_name}({args_name}):{body}\n"
    else:
        tentative_name = "%s = %s" % (tentative_name[0].strip(), function_name)
        fun_py_style = f"{init_space}def {function_name}({args_name}):{body}\n{init_space}{tentative_name}"

    py_info = {
        "fun_name": function_name,
        "args_name": args_name,
        "body": body,
        "fun_py_style": fun_py_style,
        "anonymous": anonymous,
    }
    return py_info


def func_detector(lines):
    """Detect Javascript Case1 functions in a list of lines.
    This function count the number of '{' and '}' to determinate
    the number of lines of a function in a file.

    Args:
        lines ([list]): A list with Javascript code.

    Returns:
        [list]: Return a list with Javascript code.

    Examples:
        >>> from ee_extra import func_detector
        >>> x = "var a = 2;\nfunction(x) {\n    function(y){ return y\n}\nreturn x}"
        >>> lines = x.split("\n")
        >>> func_detector(lines)
        >>> # ['var a = 2;', ['function(x) {', '    function(y) return y', '}'], 'return x}']
    """
    pattern = r".*function.*{"
    counter = 0  # curly brackets counter
    subgroup = list("0" * len(lines))
    for index, line in enumerate(lines):
        regex_result = regex.match(pattern, line)
        if regex_result or counter != 0:
            openings = len(regex.findall("{", line))
            closings = len(regex.findall("}", line))
            counter = counter + openings - closings
            subgroup[index] = "1"
    subgroups = "".join(subgroup)
    merge_rule = from_bin_to_list(subgroups)

    # Create the new x string
    final_x = list()
    for index in merge_rule:
        if isinstance(index, list):
            final_x.append([lines[index2] for index2 in index])
        else:
            final_x.append(lines[index])
    return final_x


def func_detector_recursive(lines):
    """Recursively detect nested Case1 function in a list of lines.

    Args:
        lines ([list]): A list with Javascript code as strings.

    Returns:
        [list]:  A list with Javascript code (as string) in groups.

    Examples:
        >>> from ee_extra import func_detector_recursive
        >>> x = "var a = 2;\nfunction(x) {\n    function(y) { return y\n}\nreturn x}"
        >>> lines = x.split("\n")
        >>> lines = func_detector(lines)
        >>> func_detector_recursive(lines)
        >>> # ['var a = 2;', ['function(x) {', ['    function(y) { return y', '}'], 'return x}']]
    """
    new_lines = []
    for line in lines:
        if isinstance(line, list):
            fheader, ftail = (line[0], line[-1])
            fbody = func_detector(line[1:][:-1])
            new_line = [fheader] + fbody + [ftail]
            new_lines.append(func_detector_recursive(new_line))
        else:
            new_lines.append(line)
    return new_lines


def to_fn_python(lines):
    """Apply the function 'from_js_to_py_fn_simple' to each group
       detected by 'func_detector_recursive'.

    Args:
        lines ([list]): A list with Javascript code (as string) in groups.

    Returns:
        [list]:  A non-nested list with the code translated into Python.
    Examples:
        >>> from ee_extra import to_fn_python
        >>> x = "var a = 2;\nfunction(x) {function(y) {return y}\nreturn x}"
        >>> x = beautify(x)
        >>> lines = x.split("\n")
        >>> lines = func_detector(lines)
        >>> lines = func_detector_recursive(lines)
        >>> "\n".join(to_fn_python(lines))
        >>> # 'var a = 2;
        >>> # def TJHMWsLGqNroYrB3k(x):
        >>> #     def rTYblejkWCBHZVGhY(y):
        >>> #         return y
        >>> #     return x
    """
    new_lines = list()
    for line in lines:
        if is_nested_list(line) == -1:
            new_lines.append(line)
        elif is_nested_list(line) == 0:
            fn_name = from_js_to_py_fn_simple(line)["fun_py_style"]
            new_lines.append(fn_name)
        else:
            new_lines.append(to_fn_python(line))
    if is_nested_list(new_lines):
        new_lines = to_fn_python(new_lines)
    return new_lines


def func_translate_case01(x):
    """Put everything together to translate a Javascript Case1 function into Python.

    Args:
        x ([str]): A string with Javascript code.

    Returns:
        [str]:  A string with the code translated into Python.

    Examples:
        >>> from ee_extra import func_translate_case01
        >>> x = "function(x) {return x}"
        >>> x = beautify(x)
        >>> func_translate_case01(x)
        >>> # def oeEKYeBMHkJdBAxrP(x):
        >>> #     return x
    """
    lines = x.split("\n")
    lines = func_detector(lines)
    lines = func_detector_recursive(lines)

    # testss = [index for index, line in enumerate(lines) if isinstance(line, list)]
    # for xxx in testss:
    #    to_fn_python([lines[xxx][:27]])

    return "\n".join(to_fn_python(lines))


# --------------------------------------------------------------------------
# Second Case ---------------------------------------------------------------
# --------------------------------------------------------------------------
def get_text_in_map(x):
    """
    This function count the number of '(' and ')' after a wild
    '.map(' appears in a string.

    Args:
        x (str): A string with a wild '.map('

    Returns:
        [str]: The string between '.map(' and ')'.

    Examples:
        >>> from ee_extra import get_text_in_map
        >>> x = "ic.map(function(x){return y})"
        >>> get_text_in_map(x)
    """
    subgroup = list()
    counter = 0
    for lchr in x:
        if lchr == ")":
            counter -= 1
        if counter > 0:
            subgroup.append(lchr)
        if lchr == "(":
            counter += 1
    subgroups = "".join(subgroup)
    return subgroups


def from_mapjs_to_py_fn_simple(js_function):
    """From Javascript no-nested Case2 function to Python.
    Args:
        js_function (str): A Python string
    Returns:
        [dict]: Dictionary with the following keys:
                    - fun_name: function name
                    - args_name: list of arguments names
                    - body: function body
                    - fun_py_style: function in Python.
                    - anonymous: True if the function is anonymous, 0 if not.
    Examples:
        >>> from ee_extra import from_mapjs_to_py_fn_simple
        >>> js_function = "ic2.map(function(x){return y})"
        >>> js_function = beautify(js_function)
        >>> from_mapjs_to_py_fn_simple(js_function)["fun_py_style"]
        >>> #def EvsFYLkYJHtiIj5au(x):
        >>> #    return y
        >>> #ic2.map(EvsFYLkYJHtiIj5au)
    """
    # 1. Get function header
    if isinstance(js_function, list):
        fn_header = "\n".join(js_function)
    else:
        fn_header = js_function

    # 2. get function name
    pattern = r"function\s*([\x00-\x7F][^\s]+)\s*\(.*\)\s*{"
    regex_result = regex.findall(pattern, fn_header)

    # 3. if it is a anonymous function assign a random name
    if len(regex_result) == 0:
        anonymous = True
        function_name = random_fn_name()
    else:
        anonymous = False
        function_name = "".join(regex_result[0])

    # 4. get args
    pattern = r"function\s*[\x00-\x7F][^\s]*\s*\(\s*([^)]+?)\s*\)\s*{|function\(\s*([^)]+?)\s*\)\s*"
    int_args = regex.findall(pattern, fn_header)
    if int_args == []:
        args_name = ""
    else:
        args_name = "".join(int_args[0])
        new_args = list()
        for arg in args_name.split(","):
            if "=" not in arg:
                new_args.append(arg.strip() + "='__None'")
            else:
                new_args.append(arg.strip())
        args_name = ", ".join(new_args)

    # 5. get body
    pattern = r"({(?>[^{}]+|(?R))*})"
    body = regex.search(pattern, fn_header)[0][1:-1].rstrip()

    # 6. Init space
    init_space = regex.match("\s*", fn_header)[0]

    # 7. py function info
    py_func = f"{init_space}def {function_name}({args_name}):{body}\n"
    pystring = fn_header.replace(get_text_in_map(fn_header), function_name)
    py_info = {
        "fun_name": function_name,
        "args_name": args_name,
        "body": body,
        "fun_py_style": f"{py_func}{pystring}",
        "anonymous": anonymous,
    }
    return py_info


def mapfunc_detector(lines):
    """Detect Javascript Case2 functions in a list of lines.
    The idea behind the code is count the number of '{' and '}'
    to determinate the number of lines of a function in a file.

    Args:
        lines ([list]): A list with Javascript code.

    Returns:
        [list]: Return a list with Javascript code.

    Examples:
        >>> from ee_extra import mapfunc_detector
        >>> x = "var ic = ee.ImageCollection([ee.Image(0), ee.Image(1)])"
        >>> y = "\nic.map(function(x){return x})"
        >>> z = x + y
        >>> lines = z.split("\n")
        >>> mapfunc_detector(lines)
        >>> # ['var ic = ee.ImageCollection([ee.Image(0), ee.Image(1)])',
        >>> #  ['ic.map(function(x){return x})']]
    """
    # Function detector -------------------------------------------------------
    pattern = r".*map\(.*function.*{|.*forEach\(.*function.*{"
    counter = 0  # curly brackets counter
    subgroup = list("0" * len(lines))
    for index, line in enumerate(lines):
        regex_result = regex.match(pattern, line)
        if regex_result or counter != 0:
            openings = len(regex.findall("{", line))
            closings = len(regex.findall("}", line))
            counter = counter + openings - closings
            subgroup[index] = "1"
    subgroups = "".join(subgroup)
    merge_rule = from_bin_to_list(subgroups)

    # Create the new x string
    final_x = list()
    for index in merge_rule:
        if isinstance(index, list):
            final_x.append([lines[index2] for index2 in index])
        else:
            final_x.append(lines[index])
    return final_x


def mapfunc_detector_recursive(lines):
    """Recursively detect nested Case 2 function in a list of lines.

    Args:
        lines ([list]): A list with Javascript code as strings.

    Returns:
        [list]:  A list with Javascript code (as string) in groups.

    Examples:
        >>> from ee_extra import mapfunc_detector
        >>> v = "var ic = ee.ImageCollection([ee.Image(0), ee.Image(1)])\n"
        >>> w = "ic.map(function(x){\n"
        >>> x = "print(x)\nic2.map(function(x){return y})"
        >>> y = "return x})"
        >>> z = beautify(v + w + x + y)
        >>> lines = z.split("\n")
        >>> lines = mapfunc_detector(lines)
        >>> mapfunc_detector_recursive(lines)
        >>> # [...,[...,[...]]]
    """
    new_lines = []
    for line in lines:
        if isinstance(line, list):
            fheader, ftail = (line[0], line[-1])
            fbody = mapfunc_detector(line[1:][:-1])
            new_line = [fheader] + fbody + [ftail]
            new_lines.append(mapfunc_detector_recursive(new_line))
        else:
            new_lines.append(line)
    return new_lines


def to_mapfn_python(lines):
    """Apply the function 'from_mapjs_to_py_fn_simple' to each group
       detected by 'mapfunc_detector_recursive'.

    Args:
        lines ([list]): A list with Javascript code (as string) in groups.

    Returns:
        [list]:  A non-nested list with the code translated into Python.
    Examples:
        >>> from ee_extra import to_fn_python
        >>> v = "var ic = ee.ImageCollection([ee.Image(0), ee.Image(1)])\n"
        >>> w = "ic.map(function(x){\n"
        >>> x = "print(x)\nic2.map(function(x){return y})\n"
        >>> y = "return x})"
        >>> z = beautify(v + w + x + y)
        >>> lines = z.split("\n")
        >>> lines = func_detector(lines)
        >>> lines = func_detector_recursive(lines)
        >>> "\n".join(to_mapfn_python(lines))
        >>> # var ic = ee.ImageCollection([ee.Image(0), ee.Image(1)])
        >>> # def fagvQLeZPOiW4FwWa(x):
        >>> #     print(x)
        >>> #     def OzvEuaJaPeFAXW3iN(x):
        >>> #         return y
        >>> #     ic2.map(OzvEuaJaPeFAXW3iN)
        >>> #     return x
        >>> # ic.map(fagvQLeZPOiW4FwWa)
    """
    new_lines = list()
    for line in lines:
        if is_nested_list(line) == -1:
            new_lines.append(line)
        elif is_nested_list(line) == 0:
            fn_name = from_mapjs_to_py_fn_simple(line)["fun_py_style"]
            new_lines.append(fn_name)
        else:
            new_lines.append(to_mapfn_python(line))
    if is_nested_list(new_lines):
        new_lines = to_mapfn_python(new_lines)
    return new_lines


def func_translate_case02(x):
    """Put everything together to translate a Javascript Case2 function into Python.

    Args:
        x ([str]): A string with Javascript code.

    Returns:
        [str]:  A string with the code translated into Python.

    Examples:
        >>> from ee_extra import to_fn_python
        >>> v = "var ic = ee.ImageCollection([ee.Image(0), ee.Image(1)])\n"
        >>> w = "ic.map(function(x){\n"
        >>> x = "print(x)\nic2.map(function(x){return y})\n"
        >>> y = "return x})"
        >>> z = beautify(v + w + x + y)
        >>> func_translate_case02(z)
        >>> # def fagvQLeZPOiW4FwWa(x):
        >>> #     print(x)
        >>> #     def OzvEuaJaPeFAXW3iN(x):
        >>> #         return y
        >>> #     ic2.map(OzvEuaJaPeFAXW3iN)
        >>> #     return x
        >>> # ic.map(fagvQLeZPOiW4FwWa)
    """
    lines = x.split("\n")
    lines = mapfunc_detector(lines)
    lines = mapfunc_detector_recursive(lines)
    return "\n".join(to_mapfn_python(lines))


# --------------------------------------------------------------------------
# Third case ---------------------------------------------------------------
# --------------------------------------------------------------------------
def func_translate_case03(x):
    """Solve Case3 problem

    Args:
        x ([string]): A string with Javascript code.

    Returns:
        [string]:  A string with Javascript code.

    Examples:
    >>> from ee_extra import remove_assignment_specialcase_01
    >>> text01 = "exports.addBand = function(landsat){ var wrap "
    >>> text02 = "= function(image){ return 0;} return 0;}"
    >>> text = beautify(text01 + text02)
    >>> text = normalize_fn_name(text)
    >>> func_translate_case03(text)
    >>> # def mNrjUIPHkCfPiM3pH(landsat):
    >>> #     def wrap(image):
    >>> #         return 0;
    >>> #     return 0;
    >>> # exports.addBand  = mNrjUIPHkCfPiM3pH
    """
    # does anonymous function asignation exists?
    lines = x.split("\n")

    # Does the line starts with "exports" or "eeExtraExports"?
    pattern01 = r"(?:^|\W)exports|eeExtraExports(?:$|\W)"
    lines_to_work = [
        index for index, line in enumerate(lines) if bool(regex.search(pattern01, line))
    ]
    if len(lines_to_work) == 0:
        return x
    else:
        for index in lines_to_work:
            line = lines[index]
            # Does the line inmediately assign a function?
            if bool(regex.search("=\s*function", line)):
                # Search the name
                pattern02 = "([^=]*)="
                export_str = regex.findall(pattern02, line)[0]
                rname = random_fn_name()
                pattern02 = export_str + "=.*function"
                x = regex.sub(pattern02, ("function " + rname), x)

                # add export at the end of the file
                x = x + "\n" + export_str + " = " + rname

                # Run func_translate_case01
                # x = func_translate_case01(x)
    return x


def func_translate(x):
    """Put everything together

    Args:
        x ([str]): A string with Javascript code.

    Returns:
        [str]:  A string with the code translated into Python.

    Examples:
        >>> from ee_extra import func_translate
        >>> x = "function(x) {return x}"
        >>> x = beautify(x)
        >>> func_translate(x)
        >>> # def oeEKYeBMHkJdBAxrP(x):
        >>> #     return x
    """
    x = func_translate_case03(x)
    x = func_translate_case02(x)
    x = func_translate_case01(x)
    return x
