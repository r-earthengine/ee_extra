"""Auxiliary module with functions to translate JavaScript scripts to Python."""

import textwrap

from ee_extra import translate_functions as tfunc
from ee_extra import translate_general as tgnrl
from ee_extra import translate_jsm_main as tjsm
from ee_extra import translate_loops as tloops
from ee_extra import translate_utils as tutils
from ee_extra.JavaScript.utils import _check_regex
from ee_extra.JavaScript.utils import _check_jsbeautifier


def inside_quoation_marks(x, word):
    regex = _check_regex()
    pattern = r"([\"'])(?:(?=(\\?))\2.)*?\1"
    if regex.search(pattern, x):
        qm_word = regex.search(pattern, x).group(0)
        return word in qm_word
    else:
        return False


def fix_typeof(x):
    """Change typeof lesly to typeof(lesly)

    Args:
        x (str): A string with Javascript syntax.

    Returns:
        [str]: Python string

    Examples:
        >>> from ee_extra import fix_typeof
        >>> fix_typeof("typeof lesly")
        >>> # typeof(lesly)
    """
    regex = _check_regex()
    lazy_cond = r"typeof\s*\(*[A-Za-z0-9Α-Ωα-ωίϊΐόάέύϋΰήώ\[\]_]*\)*"
    typeof_cases = regex.findall(lazy_cond, x)
    if typeof_cases == []:
        return x, ""
    else:
        for typeof_case in typeof_cases:
            x = x.replace(typeof_case, "typeof(%s)" % typeof_case.split(" ")[1])
    header = """

    # Javascript typeof wrapper ---------------------------------------
    def typeof(x):
        # Python version of Javascript typeof
        if x == '__None':
            return "undefined"
        elif x == None:
            return "object"
        elif isinstance(x, bool):
            return "boolean"
        elif isinstance(x, (int, float)):
            return "number"
        elif isinstance(x, str):
            return "string"
        elif hasattr(x, '__call__'):
            return "function"
        else:
            return "object"
    # -----------------------------------------------------------------
    """
    return x, textwrap.dedent(header)


# maybe we can do it better, but for now it should works
def fix_sugar_if(x):
    """
    Change [if (condition) ? true_value : false_value] -->
           [true_value if condition else false_value]

    Args:
        x (str): A string with Javascript syntax.

    Returns:
        [str]: Python string

    Examples:
        >>> from ee_extra import fix_sugar_if
        >>> fix_sugar_if("maskThese = (typeof msk !== 'undefined') ?  msk : [];")
        >>> # maskThese = msk if (typeof msk !== 'undefined') else [];
    """
    regex = _check_regex()
    lines = x.split("\n")
    condition01 = r"\(.*\)\s\?\s\w+\s:.*"  # search for sugar strings
    sugar_lines = [line for line in lines if regex.search(condition01, line)]

    if sugar_lines == []:
        return x
    else:
        for sugar_line in sugar_lines:
            if " = " in sugar_line:
                # initial space
                whitespace_cond = r"^\s*"
                init_space = regex.findall(whitespace_cond, sugar_line)[0]

                # is there a assignment?
                condition02 = r"(.*)\s+=\s+"
                matches = regex.findall(condition02, sugar_line, regex.MULTILINE)
                varname = matches[0].strip() + " = "
            else:
                varname = ""
            # sugar syntax is: if (condition) ? true_value : false_value
            condition03 = r"=(.*)\?(.*):(.*)"
            ifcondition, dotrue, dofalse = regex.findall(
                condition03, sugar_line, regex.MULTILINE
            )[0]

            # fix the if condition
            ifcondition = ifcondition.strip()
            new_line = "%s%s%s if %s else %s" % (
                init_space,
                varname,
                dotrue.strip(),
                ifcondition,
                dofalse.strip(),
            )
            x = x.replace(sugar_line, new_line)
    return x


def normalize_fn_name(x: str) -> str:
    """Normalize Javascript function name

    var xx = function(x){} --> function xx(x){}

    Args:
        x (str): A string with Javascript syntax.

    Returns:
        [str]: Python string

    Examples:
        >>> from ee_extra import normalize_fn_name
        >>> normalize_fn_name("var exp = function(x){'hi'}")
        >>> # function exp(x){'hi'}
    """
    regex = _check_regex()
    pattern = r"var\s*(.*[^\s])\s*=\s*function"
    matches = regex.finditer(pattern, x, regex.MULTILINE)
    for _, item in enumerate(matches):
        match = item.group(0)
        group = item.group(1)
        x = x.replace(match, f"function {group}")
    return x


def change_operators(x):
    """Change logical operators, boolean, null and comments

        m = s.and(that); -> m = s.And(that)

    Args:
        x (str): A string with Javascript syntax.

    Returns:
        [str]: Python string

    Examples:
        >>> from ee_extra import change_operators
        >>> change_operators("s.and(that);")
        >>> # m = s.And(that)
    """
    regex = _check_regex()
    from collections import OrderedDict

    reserved = OrderedDict(
        {
            "===": " == ",
            "!==": " != ",
            r"\.and\(": ".And(",
            r"\.or\(": ".Or(",
            r"\.not\(": ".Not(",
            r"(?<![a-zA-Z])true(?![a-zA-Z])": "True",
            r"(?<![a-zA-Z])false(?![a-zA-Z])": "False",
            r"(?<![a-zA-Z])null(?![a-zA-Z])": "None",
            r"//": "#",
            r"!(\w)": " not ",
            r"\|\|": " or ",
        }
    )

    for key, item in reserved.items():
        x = regex.sub(key, item, x)
    # Correct https://
    x = x.replace("https:#", "https://")
    x = x.replace("http:#", "http://")
    return x


def fix_multiline_comments(x):
    """Replace "/*" or "*/ by "#".

    Args:
        x (str): A string with Javascript syntax.

    Returns:
        [str]: Python string

    Examples:
        >>> from ee_extra import fix_multiline_comments
        >>> fix_multiline_comments("/* hola lesly */")
        >>> # # hola lesly */
    """
    regex = _check_regex()
    pattern = r"/\*(.*?)\*/"
    matches = regex.findall(pattern, x, regex.DOTALL)
    if matches == []:
        return x
    for match in matches:
        x = x.replace(match, match.replace("\n", "\n#"))
    x = x.replace("/*", "#")
    return x


def delete_inline_comments(x):
    """Delete comments inline

    lesly.add(0) # holi --> lesly.add(0)

    Args:
        x (str): A string with Javascript syntax.

    Returns:
        [str]: Python string

    Examples:
        >>> from ee_extra import delete_inline_comments
        >>> delete_inline_comments('var x = \n ee.Image(0) # lesly')
        >>> # var x = \n ee.Image(0)
    """
    lines = x.split("\n")
    newlines = []
    for line in lines:
        if line == "":
            newlines.append("")
            continue
        if line[0] == "#":
            newlines.append(line)
        else:
            if "#" in line:
                michi_index = [index for index, lchr in enumerate(line) if lchr == "#"][
                    0
                ]
                newlines.append(line[:michi_index].rstrip())
            else:
                newlines.append(line)
    return "\n".join(newlines)


def line_starts_with_dot(x):
    """If a line starts with a dot, merge with the previous line.

    var csaybar = ee.Image(0)  --> var csaybar = ee.Image(0).add(10)
                    .add(10)

    Args:
        x (str): A string with Javascript syntax.

    Returns:
        [str]: Python string

    Examples:
        >>> from ee_extra import line_starts_with_dot
        >>> line_starts_with_dot("var cesar = ee.Image(0)\n    .add(10)\n    .add(100)")
        >>> # 'var cesar = ee.Image(0).add(10).add(100)'
    """
    # get True is "." is the first character
    def first_is_dot(x):
        if x == "":
            return False
        else:
            return x[0] == "."

    # Remove all whitespace at the end.
    lines = [line.rstrip() for line in x.split("\n")]

    # Get "1" is the first chr is "." otherwise get "0"
    is_first_chr_dot = list()
    for index, line in enumerate(lines):
        if line != "":
            cond = str(int(first_is_dot(line.strip())))
        else:
            try:
                nextline = lines[index + 1]
                ncond = str(int(first_is_dot(nextline.strip())))
                if ncond == "1":
                    cond = "1"
                else:
                    cond = "0"
            except IndexError:
                cond = "0"
        is_first_chr_dot.append(cond)
    subgroups = "".join(is_first_chr_dot)  # e.g. "011000100"

    # If no "." at the begining, then return the original string
    if int(subgroups) == 0:
        return x

    # If the next line starts with ".", merge with the previous line.
    merge_rule = tgnrl.subgroups_creator_bef(subgroups)

    # Create the new x string
    final_x = list()
    for index in merge_rule:
        if isinstance(index, list):
            final_merge = list()
            for enum, index2 in enumerate(index):
                if enum == 0:
                    final_merge.append(lines[index2])
                else:
                    final_merge.append(lines[index2].strip())
            final_x.append("".join(final_merge))
        else:
            final_x.append(lines[index])
    return "\n".join(final_x)


def ends_with_plus(x):
    """If a line ends in a "+", merge with the next line.

    "hola" + \n "mundo"  --> "hola" + "mundo"

    Args:
        x (str): A string with Javascript syntax.

    Returns:
        [str]: Python string

    Examples:
        >>> from ee_extra import ends_with_plus
        >>> ends_with_plus('"hola" + \n "mundo"')
        >>> # '"hola" + "mundo"'
    """
    # get True is "+" is the last character
    def last_is_plus(x):
        if x == "":
            return False
        else:
            return x[-1] == "+"

    # Remove all whitespace at the end.
    lines = [line.rstrip() for line in x.split("\n")]

    # Get "1" is the last chr is "+" otherwise get "0"
    is_last_chr_plus = list()
    for line in lines:
        if len(line) > 0:
            cond = str(int(last_is_plus(line.strip())))
        else:
            cond = "0"
        is_last_chr_plus.append(cond)
    subgroups = "".join(is_last_chr_plus)  # e.g. "011000100"

    # If no "+", then return the original string
    if int(subgroups) == 0:
        return x

    # Merge the current line with the next line if '10'
    merge_rule = tgnrl.subgroups_creator_aft(subgroups)

    # Create the new x string
    final_x = list()
    for index in merge_rule:
        if isinstance(index, list):
            final_x.append("".join([lines[index2] for index2 in index]))
        else:
            final_x.append(lines[index])
    return "\n".join(final_x)


def ends_with_equal(x):
    """If a line ends in a "=", merge with the next line.

    var x = \n ee.Image(0)  --> var x = ee.Image(0)

    Args:
        x (str): A string with Javascript syntax.

    Returns:
        [str]: Python string

    Examples:
        >>> from ee_extra import ends_with_equal
        >>> ends_with_equal('var x = \n ee.Image(0)')
        >>> # var x = ee.Image(0)
    """
    # get True is "=" is the last character
    def last_is_equal(x):
        if x == "":
            return False
        else:
            return x[-1] == "="

    # Remove all whitespace at the end.
    lines = [line.rstrip() for line in x.split("\n")]

    # Get "1" is the last chr is "=" otherwise get "0"
    is_last_chr_plus = list()
    for line in lines:
        if len(line) > 0:
            cond = str(int(last_is_equal(line)))
        else:
            cond = "0"
        is_last_chr_plus.append(cond)
    subgroups = "".join(is_last_chr_plus)  # e.g. "011000100"

    # If no "=", then return the original string
    if int(subgroups) == 0:
        return x

    # Merge the current line with the next line if '10'
    merge_rule = tgnrl.subgroups_creator_aft(subgroups)

    # Create the new x string
    final_x = list()
    for index in merge_rule:
        if isinstance(index, list):
            final_x.append("".join([lines[index2] for index2 in index]))
        else:
            final_x.append(lines[index])
    return "\n".join(final_x)


def fix_str_plus_int(x):
    """Change str + int by str + str(int)

    Args:
        x (str): The string to be fixed

    Returns:
        str: The fixed string

    Examples:
        >>> from ee_extra import fix_str_plus_int
        >>> fix_str_plus_int('"hola" + "mundo" + 10000')
        >>> # '"hola" |plus| "mundo" |plus| str(10000)'
    """
    # Header Infix operator class to add if the '+' operator exists.
    header = """
    # Javascript sum module -------------------------------------------------------
    class Infix:
        def __init__(self, function):
            self.function = function
        def __ror__(self, other):
            return Infix(lambda x, self=self, other=other: self.function(other, x))
        def __or__(self, other):
            return self.function(other)
        def __rlshift__(self, other):
            return Infix(lambda x, self=self, other=other: self.function(other, x))
        def __rshift__(self, other):
            return self.function(other)
        def __call__(self, value1, value2):
            return self.function(value1, value2)

    def __eextra_plus(*args):
        try:
            sum_container = 0
            for arg in args:
                sum_container = sum_container + arg
        except:
            sum_container = ""
            args = [str(arg) for arg in args]
            for arg in args:
                sum_container = sum_container + arg
        return sum_container

    plus = Infix(__eextra_plus)
    # -----------------------------------------------------------------------------
    """
    # does '+' operator exist on the code?
    newx = tutils.replace_non_quoted(x, [("+", "|plus|")])
    if newx != x:
        return newx, textwrap.dedent(header)
    return x, ""


def fix_identation(x):
    """Fix Python string identation

    Args:
        x (str): A string with Python syntax.

    Returns:
        [str]: Python string

    Examples:
        >>> from ee_extra import fix_identation
        >>> fix_identation("if(i==10){\ni}")
    """
    regex = _check_regex()
    ident_base = "    "
    brace_counter = 0

    # if first element of the string is \n remove!
    if x[0] == "\n":
        x = x[1:]

    # remove multiple \n by just one
    pattern = r"\n+"
    x = regex.sub(pattern, r"\n", x)

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
    """Add extra identation in a Python function body

    Args:
        x (str): A string with Python syntax.

    Returns:
        [str]: Python string

    Examples:
        >>> from ee_extra import add_identation
        >>> add_identation("if(i==10){\ni}")
    """
    regex = _check_regex()
    pattern = "\n"
    # identation in the body
    body_id = regex.sub(pattern, r"\n    ", x)
    # identation in the header
    return "\n    " + body_id


def remove_extra_spaces(x):
    r"""Remove \n and \s if they are at the begining of the string"""
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


# 7. Change "{x = 1}" by "{'x' = 1}".
def dictionary_keys(x):
    regex = _check_regex()
    pattern = r"{(.*?)}"  # Get the data inside curly brackets
    dicts = regex.findall(pattern, x, regex.DOTALL)
    if len(dicts) > 0:
        for dic in dicts:
            items = dic.split(",")
            for item in items:
                pattern = r"(.*?):(.*)"
                item = regex.findall(pattern, item)
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

    regex = _check_regex()

    def inside_quoation_marks(x, word):
        pattern = r"([\"'])(?:(?=(\\?))\2.)*?\1"
        if regex.search(pattern, x):
            qm_word = regex.search(pattern, x).group(0)
            return word in qm_word
        else:
            return False

    if inside_quoation_marks(match, word):
        return x
    else:
        return x.replace(word, new_word)


def dictionary_object_access(x):
    """Replace <name01>.<name02> only when name01 is a dictionary"""
    regex = _check_regex()

    # Search in all lines .. it matchs <name>.<name>
    pattern = r"^(?=.*[\x00-\x7F][^\s]+\.[\x00-\x7F][^\s]+)(?!.*http).*$"
    matches = regex.findall(pattern, x, regex.MULTILINE)
    matches.sort(reverse=True)

    # match = matches[7]
    for match in matches:
        if len(match) > 0:
            if match[0] == "#":
                continue

        # Search in one specific line.
        pattern1 = (
            r"[A-Za-z0-9Α-Ωα-ωίϊΐόάέύϋΰήώ\[\]_]+\.[A-Za-z0-9Α-Ωα-ωίϊΐόάέύϋΰήώ\[\]_]+"
        )
        pattern2 = pattern1 + "."

        # This bunch of code take a decision based on the next letter. However, if the
        # next letter is a \n it could cause problems. When this happens we add a ')' to
        # the end of the line.
        matches_at_line1 = regex.findall(pattern1, match)
        matches_at_line2 = regex.findall(pattern2, match)

        matches_at_line = list()
        for m1, m2 in zip(matches_at_line1, matches_at_line2):
            if m1 == m2:
                matches_at_line.append(m2 + ")")
            else:
                matches_at_line.append(m2)

        # remove square brackets (It is important to fix ee.Geometry.* issues)
        matches_at_line = [x.replace("]", "").replace("[", "") for x in matches_at_line]

        # match_line = matches_at_line[0]
        for match_line in matches_at_line:
            # If is a number pass
            if is_float(match_line[:-1]):
                continue

            # If is a method or a function, does not consider Math.* methods
            if (("(" in match_line[-1]) or ("ee." in match_line[:-1])) and (
                not "Math." in match_line
            ):
                continue

            # If is a math
            if "Math." in match_line:
                new_word = match_line.lower()
                x = dict_replace(x, match, match_line, new_word)
            else:
                nlist = match_line[:-1].split(".")
                arg_nospace = regex.sub(r"\s", "", nlist[1])
                new_word = '%s["%s"]' % (nlist[0], arg_nospace)
                x = dict_replace(x, match, match_line[:-1], new_word)
    return x


# Change "f({x = 1})" por "f(**{x = 1})"
def keyword_arguments_object(x):
    regex = _check_regex()
    pattern = r"(\w+)\({(.*?)}\)"
    matches = regex.findall(pattern, x, regex.DOTALL)

    # eliminate is the method is getThumbURL|getDownloadURL|getThumbId.
    matches = [
        params
        for fname, params in matches
        if fname not in ["getThumbURL", "getDownloadURL", "getThumbId"]
    ]

    matches = list(
        set(matches)
    )  # Remove duplicate matches (See Test:test_line_breaks01)

    if len(matches) > 0:
        for match in matches:
            x = x.replace("{" + match + "}", "**{" + match + "}")
    pattern = r"ee\.Dictionary\(\*\*{"
    matches = regex.findall(pattern, x, regex.DOTALL)
    matches = list(
        set(matches)
    )  # Remove duplicate matches (See Test:test_line_breaks01)
    if len(matches) > 0:
        for match in matches:
            x = x.replace(match, "ee.Dictionary({")
    return x


# Change "if(x){" por "if x:"
def if_statement(x):
    regex = _check_regex()
    pattern = r"}(.*?)else(.*?)if(.*?){"
    matches = regex.findall(pattern, x)
    if len(matches) > 0:
        for match in matches:
            match = list(match)
            x = x.replace(
                "}" + match[0] + "else" + match[1] + "if" + match[2] + "{",
                f"elif {match[2]}:",
            )
    pattern = r"if(.*?)\((.*)\)(.*){"
    matches = regex.findall(pattern, x)
    if len(matches) > 0:
        for match in matches:
            match = list(match)
            x = x.replace(
                "if" + match[0] + "(" + match[1] + ")" + match[2] + "{",
                f"if {match[1]}:",
            )
    pattern = r"}(.*?)else(.*?){"
    matches = regex.findall(pattern, x)
    if len(matches) > 0:
        for match in matches:
            match = list(match)
            x = x.replace("}" + match[0] + "else" + match[1] + "{", "else:")
    return tgnrl.delete_brackets(x)


# Change "Array.isArray(x)" por "isinstance(x,list)"
def array_isArray(x):
    regex = _check_regex()
    pattern = r"Array\.isArray\((.*?)\)"
    matches = regex.findall(pattern, x)
    if len(matches) > 0:
        for match in matches:
            x = x.replace(f"Array.isArray({match})", f"isinstance({match},list)")
    return x


def add_exports(x):
    regex = _check_regex()
    if regex.search("exports|eeExtraExports", x):
        header = """
        class AttrDict(dict):
            def __init__(self, *args, **kwargs):
                super(AttrDict, self).__init__(*args, **kwargs)
                self.__dict__ = self
        exports = AttrDict()
        """
        return textwrap.dedent(header)
    else:
        return ""


def add_header(x, header_list=""):
    py_packages = "import ee\nimport warnings\nimport math\nimport inspect\nimport locale\nimport regex\n"
    header_list.append(py_packages)
    header_list.reverse()
    return "\n".join(header_list) + "\n" + x


def remove_single_declarations(x):
    regex = _check_regex()
    condition = r"var\s[A-Za-z0-9Α-Ωα-ωίϊΐόάέύϋΰήώ\[\]_]+;*\n"
    x = regex.sub(condition, "", x)
    return x

def remove_documentation(x):
    regex = _check_regex()
    # remove // only if it is not in a string
    condition = r"\/\/(?=(?:[^\"']*\"[^\"']*\")*[^\"']*$).*"
    newx = regex.sub(condition, "", x, flags=regex.MULTILINE)
    return newx


def translate(x: str, black: bool = False, quiet: bool = True) -> str:
    """Translates a JavaScript script to a Python script.

    Args:
        x : A JavaScript script.

    Returns:
        A Python script.

    Examples:
        >>> import ee
        >>> from ee_extra import translate
        >>> translate("var x = ee.ImageCollection('COPERNICUS/S2_SR')")
    """
    regex = _check_regex()
    beautify, default_options = _check_jsbeautifier()

    opts = default_options()
    opts.keep_array_indentation = True

    header_list = list()
    # 1. reformat and re-indent ugly JavaScript
    x = remove_documentation(x)  # remove documentation
    x = remove_single_declarations(x)  # remove declarations
    x = beautify(x, opts)

    # 2. Fix typeof change typeof x to typeof(x)
    x, header = fix_typeof(x)
    header_list.append(header)

    # 3. Fix JavaScript methods
    x, header = tjsm.translate_jsmethods(x)
    header_list.append(header)

    # 4. reformat Js function definition style (from var fun = function(bla, bla) -> function fun(bla, bla)).
    x = normalize_fn_name(x)
    # 5. Remove var keyword.
    x = tgnrl.var_remove(x)
    # 6. Change logical operators, boolean, null, comments and others.
    x = change_operators(x)
    # 7. Change multiline jscript comments to just '#'.
    x = fix_multiline_comments(x)
    # 8. If line starts with ".", then merge it with the previous one.
    x = line_starts_with_dot(x)
    # 9. If a line ends with "+", then merge it with the next one.
    x = ends_with_plus(x)
    # 10. If a line ends with "=", then merge it with the next one.
    x = ends_with_equal(x)

    x = x.replace("\nfunction ", "\n\nfunction ")
    x = tfunc.func_translate(x)

    # 11. Change e.g. "for(var i = 0;i < x.length;i++)" to "for i in range(0,len(x),1):"
    x = tloops.fix_for_loop(x)
    # 12. Change e.g. "while (i > 10)" to "while i>10:"
    x = tloops.fix_while_loop(x)
    # 13. Change lines like var i++ to var i = i + 1.
    x = tloops.fix_inline_iterators(x)

    x = if_statement(x)

    # 14. Delete extra brackets.
    x = tgnrl.delete_brackets(x)

    # 15. Change [if (condition) ? true_value : false_value] to [true_value if condition else false_value]
    # OBS: fix_sugar_if must always to if_statement to avoid conflicts.
    x = fix_sugar_if(x)

    x = dictionary_keys(x)
    x = dictionary_object_access(x)
    x = keyword_arguments_object(x)
    x = array_isArray(x)
    header_list.append(add_exports(x))
    x = x.replace(";", "")
    if black:
        try:
            from black import FileMode, format_str
            x = format_str(x, mode=FileMode())
        except ImportError:
            raise ImportError(
                '"black" is not installed. Please install "black" when using "black=True" -> "pip install black"'
            )
    x, header = fix_str_plus_int(x)
    header_list.append(header)
    x = add_header(x, header_list)
    return x