import regex


def translate_string_charAt(x):
    """Converts string.charAt(index) to __ee_extra_string_charAt(string, index)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_string_charAt
        >>> translate_string_charAt("'hello'.charAt(0)")
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    condition01 = "([\w|'|\"]+)?\.charAt\(.*\)"
    condition02 = "([\w|'|\"]+?\.charAt\(.*\))"
    condition03 = "[\w|'|\"]+?\.charAt\((.*)\)"

    var_names = regex.findall(condition01, x)
    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    replacement = regex.findall(condition02, x)
    arg_names = regex.findall(condition03, x)

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_string_charAt(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_string_concat(x):
    """Converts string.concat(string1, string2, ...) to
    __ee_extra_string_concat(string, string1, string2, ...)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_string_concat
        >>> translate_string_concat("'hello'.concat('world', 'lalesly')")
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    condition01 = "([\w|'|\"]+)?\.concat\(.*\)"
    condition02 = "([\w|'|\"]+?\.concat\(.*\))"
    condition03 = "[\w|'|\"]+?\.concat\((.*)\)"
    var_names = regex.findall(condition01, x)

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    replacement = regex.findall(condition02, x)
    arg_names = regex.findall(condition03, x)

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_string_concat(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_string_indexOf(x):
    """Converts string.indexOf(string) to __ee_extra_string_indexOf(string, string)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_string_concat
        >>> translate_string_concat("'hello'.concat('world', 'lalesly')")
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    condition01 = "([\w|'|\"]+)?\.indexOf\(.*\)"
    condition02 = "([\w|'|\"]+?\.indexOf\(.*\))"
    condition03 = "[\w|'|\"]+?\.indexOf\((.*)\)"
    var_names = regex.findall(condition01, x)

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    replacement = regex.findall(condition02, x)
    arg_names = regex.findall(condition03, x)

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_string_indexOf(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_string_lastIndexOf(x):
    """Converts string.lastIndexOf(string) to
    __ee_extra_string_lastIndexOf(string, string)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_string_lastIndexOf
        >>> translate_string_lastIndexOf("'daniel'.lastIndexOf('s')")
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    condition01 = "([\w|'|\"]+)?\.lastIndexOf\(.*\)"
    condition02 = "([\w|'|\"]+?\.lastIndexOf\(.*\))"
    condition03 = "[\w|'|\"]+?\.lastIndexOf\((.*)\)"
    var_names = regex.findall(condition01, x)

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    replacement = regex.findall(condition02, x)
    arg_names = regex.findall(condition03, x)

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_string_lastIndexOf(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_string_localeCompare(x):
    """Converts string.localeCompare(compareString) to
    __ee_extra_string_localeCompare(string, compareString)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_string_localeCompare
        >>> translate_string_localeCompare('"hi".localeCompare("s")')
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    condition01 = "([\w|'|\"]+)?\.localeCompare\(.*\)"  # varname
    condition02 = "([\w|'|\"]+?\.localeCompare\(.*\))"  # the full string to replace
    condition03 = "[\w|'|\"]+?\.localeCompare\((.*)\)"  # the arguments
    var_names = regex.findall(condition01, x)

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    replacement = regex.findall(condition02, x)
    arg_names = regex.findall(condition03, x)

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_string_localeCompare(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_string_length(x):
    """Converts string.length to __ee_extra_string_length(string)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_string_length
        >>> translate_string_length('myfuc(lesly.length, 10)')
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    condition01 = "([\w|'|\"]+)?\.length(?:$|\W)"
    condition02 = "([\w|'|\"]+?\.length(?:$|\W))"

    var_names = regex.findall(condition01, x)

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    replacement = [regex.sub(",|;|\)|}", "", r) for r in regex.findall(condition02, x)]

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_string_length(%s)" % var_name for var_name in var_names
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_string_match(x):
    """Converts string.match(regexp) to __ee_extra_string_match(string, regexp)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_string_match
        >>> translate_string_match(x = '"hi".match("h")')
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    condition01 = "([\w|'|\"]+)?\.match\(.*\)"  # varname
    condition02 = "([\w|'|\"]+?\.match\(.*\))"  # the full string to replace
    condition03 = "[\w|'|\"]+?\.match\((.*)\)"  # the arguments
    var_names = regex.findall(condition01, x)

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    replacement = regex.findall(condition02, x)
    arg_names = regex.findall(condition03, x)

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_string_match(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_string_search(x):
    """Converts string.search(regexp) to __ee_extra_string_search(string, regexp)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_string_search
        >>> translate_string_search(x = '"hi".search("h")')
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    condition01 = "([\w|'|\"]+)?\.search\(.*\)"  # varname
    condition02 = "([\w|'|\"]+?\.search\(.*\))"  # the full string to replace
    condition03 = "[\w|'|\"]+?\.search\((.*)\)"  # the arguments
    var_names = regex.findall(condition01, x)

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    replacement = regex.findall(condition02, x)
    arg_names = regex.findall(condition03, x)

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_string_search(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_string_slice(x):
    """Converts string.slice(start, end) to __ee_extra_string_slice(string, start, end)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_string_slice
        >>> translate_string_slice(x = '"hilesly".slice(1,3)')
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    condition01 = "([\w|'|\"]+)?\.slice\(.*\)"  # varname
    condition02 = "([\w|'|\"]+?\.slice\(.*\))"  # the full string to replace
    condition03 = "[\w|'|\"]+?\.slice\((.*)\)"  # the arguments
    var_names = regex.findall(condition01, x)

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    replacement = regex.findall(condition02, x)
    arg_names = regex.findall(condition03, x)

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_string_slice(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_string_substr(x):
    """Converts string.substr(start, length)
    to __ee_extra_string_substr(string, start, length)
    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_string_substr
        >>> translate_string_substr(x = '"leslywashere".substr(2, 4)')
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    condition01 = "([\w|'|\"]+)?\.substr\(.*\)"  # varname
    condition02 = "([\w|'|\"]+?\.substr\(.*\))"  # the full string to replace
    condition03 = "[\w|'|\"]+?\.substr\((.*)\)"  # the arguments
    var_names = regex.findall(condition01, x)

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    replacement = regex.findall(condition02, x)
    arg_names = regex.findall(condition03, x)

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_string_substr(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_string_substring(x):
    """Converts string.substring(start, length)
    to __ee_extra_string_substring(string, start, length)
    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_string_substring
        >>> translate_string_substring(x = '"leslywashere".substring(2, 4)')
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    condition01 = "([\w|'|\"]+)?\.substring\(.*\)"  # varname
    condition02 = "([\w|'|\"]+?\.substring\(.*\))"  # the full string to replace
    condition03 = "[\w|'|\"]+?\.substring\((.*)\)"  # the arguments
    var_names = regex.findall(condition01, x)

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    replacement = regex.findall(condition02, x)
    arg_names = regex.findall(condition03, x)

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_string_substring(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_string_toLowerCase(x):
    """Converts string.toLowerCase() to __ee_extra_string_toLowerCase(string)
    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_string_toLowerCase
        >>> translate_string_toLowerCase(x = '"LesLywashere".toLowerCase()')
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    condition01 = "([\w|'|\"]+)?\.toLowerCase|toLocaleLowerCase\(.*\)"  # varname
    condition02 = "([\w|'|\"]+?\.toLowerCase|toLocaleLowerCase\(.*\))"  # the full string to replace
    var_names = regex.findall(condition01, x)

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    replacement = regex.findall(condition02, x)

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_string_toLowerCase(%s)" % (var_name) for var_name in var_names
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_string_toUpperCase(x):
    """Converts string.toUpperCase() to __ee_extra_string_toUpperCase(string)
    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_string_toUpperCase
        >>> translate_string_toUpperCase(x = '"LesLywashere".toUpperCase()')
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    condition01 = "([\w|'|\"]+)?\.toUpperCase|toLocaleUpperCase\(.*\)"  # varname
    condition02 = "([\w|'|\"]+?\.toUpperCase|toLocaleUpperCase\(.*\))"  # the full string to replace
    var_names = regex.findall(condition01, x)

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    replacement = regex.findall(condition02, x)

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_string_toUpperCase(%s)" % (var_name) for var_name in var_names
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_string_toString(x):
    """Converts string.toString() to __ee_extra_string_toString(string)
    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_string_toString
        >>> translate_string_toString(x = 'var lesly=10\nlesly.toString()')
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    condition01 = "([\w|'|\"]+)?\.toString\(.*\)"  # varname
    condition02 = "([\w|'|\"]+?\.toString\(.*\))"  # the full string to replace
    var_names = regex.findall(condition01, x)

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    replacement = regex.findall(condition02, x)

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_string_toString(%s)" % (var_name) for var_name in var_names
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_string_trim(x):
    """Converts string.trim() to __ee_extra_string_trim(string)
    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_string_trim
        >>> translate_string_trim(x = ' lesly   ')
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    condition01 = "([\w|'|\"]+)?\.trim\(.*\)"  # varname
    condition02 = "([\w|'|\"]+?\.trim\(.*\))"  # the full string to replace
    var_names = regex.findall(condition01, x)

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    replacement = regex.findall(condition02, x)

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_string_trim(%s)" % (var_name) for var_name in var_names
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_string_charCodeAt(x):
    """Converts string.charCodeAt(index) to __ee_extra_string_charCodeAt(string, index)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_string_charCodeAt
        >>> translate_string_charCodeAt("'hello'.charCodeAt(0)")
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    condition01 = "([\w|'|\"]+)?\.charCodeAt\(.*\)"
    condition02 = "([\w|'|\"]+?\.charCodeAt\(.*\))"
    condition03 = "[\w|'|\"]+?\.charCodeAt\((.*)\)"

    var_names = regex.findall(condition01, x)
    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    replacement = regex.findall(condition02, x)
    arg_names = regex.findall(condition03, x)

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_string_charCodeAt(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


# Local functions to add to the final script
def local_string_charCodeAt():
    x = """
    def __ee_extra_string_charCodeAt(string, index):
        vars_name = varName(string)
        if isinstance(string, str):
            return ord(string[index])
        return eval("%s.charAt(%s)" % (vars_name, index))
    """
    return x.replace("\n    ", "\n")


def local_string_varname():
    x = """
    def varName(var):
        lcls = inspect.stack()[2][0].f_locals
        for name in lcls:
            if id(var) == id(lcls[name]):
                return name
        return None
    """
    return x.replace("\n    ", "\n")


def local_string_charAt():
    x = """
    def __ee_extra_string_charAt(string, index):
        vars_name = varName(string)
        if isinstance(string, str):
            return string[index]
        return eval("%s.charAt(%s)" % (vars_name, index))
    """
    return x.replace("\n    ", "\n")


def local_string_concat():
    x = """
    def __ee_extra_string_concat(string, *args):
        vars_name = varName(string)
        if isinstance(string, str):
            return string + "".join(args)
        args = [str(arg)for arg in args]
        return eval("%s.concat(%s)" % (vars_name, ", ".join(args)))
    """
    return x.replace("\n    ", "\n")


def local_string_indexOf():
    x = """
    def __ee_extra_string_indexOf(string, start):
        vars_name = varName(string)
        if isinstance(string, str):
            search_string = regex.search(start, string)
            if search_string is None:
                return -1
            return search_string.start()                    
        return eval("%s.indexOf(%s)" % (vars_name, start))    
    """
    return x.replace("\n    ", "\n")


def local_string_lastIndexOf():
    x = """
    def __ee_extra_string_lastIndexOf(string, start):
        vars_name = varName(string)
        if isinstance(string, str):
            search_string = regex.search(start, string[::-1])
            if search_string is None:
                return -1
            return len(string) - search_string.start() - 1
        return eval("%s.lastIndexOf(%s)" % (vars_name, start))    
    """
    return x.replace("\n    ", "\n")


def local_string_localeCompare():
    x = """
    def __ee_extra_string_localeCompare(string, compareString):
        vars_name = varName(string)
        if isinstance(string, str):
            return locale.strcoll(string.lower(), compareString.lower())
        return eval("%s.localeCompare(%s)" % (vars_name, compareString))    
    """
    return x.replace("\n    ", "\n")


def local_string_length():
    x = """
    def __ee_extra_string_length(string):
        vars_name = varName(string)
        if isinstance(string, str):
            return len(string)
        return eval("%s.length" % vars_name)    
    """
    return x.replace("\n    ", "\n")


def local_string_match():
    x = """
    def __ee_extra_string_match(string, regexp):
        vars_name = varName(string)
        if isinstance(string, str):
            if regex.match(regexp, string) is None:
                return None
            return regex.match(regexp, string).group()
        return eval("%s.match(%s)" % (vars_name, regexp))    
    """
    return x.replace("\n    ", "\n")


def local_string_search():
    x = """
    def __ee_extra_string_search(string, regexp):
        vars_name = varName(string)
        if isinstance(string, str):
            if regex.search(regexp, string) is None:
                return None
            return regex.search(regexp, string).start()
        return eval("%s.search(%s)" % (vars_name, regexp))    
    """
    return x.replace("\n    ", "\n")


def local_string_slice():
    x = """
    def __ee_extra_string_slice(string, *args):
        vars_name = varName(string)
        if isinstance(string, str):
            return string[slice(*args)]
        args = [str(arg)for arg in args]
        return eval("%s.slice(%s)" % (vars_name, ", ".join(args)))    
    """
    return x.replace("\n    ", "\n")


def local_string_substr():
    x = """
    def __ee_extra_string_substr(string, start, length):
        vars_name = varName(string)
        if isinstance(string, str):
            return string[start:][:(length -1)]
        return eval("%s.substr(%s, %s)" % (vars_name, start, length))    
    """
    return x.replace("\n    ", "\n")


def local_string_substring():
    x = """
    def __ee_extra_string_substring(string, start, end):
        vars_name = varName(string)
        if isinstance(string, str):
            return string[start:end]
        return eval("%s.substring(%s, %s)" % (vars_name, start, end))    
    """
    return x.replace("\n    ", "\n")


def local_string_toLowerCase():
    x = """
    def __ee_extra_string_toLowerCase(string):
        vars_name = varName(string)
        if isinstance(string, str):
            return string.lower()
        return eval("%s.toLowerCase()" % vars_name)    
    """
    return x.replace("\n    ", "\n")


def local_string_toUpperCase():
    x = """
    def __ee_extra_string_toUpperCase(string):
        vars_name = varName(string)
        if isinstance(string, str):
            return string.upper()
        return eval("%s.toUpperCase()" % vars_name)    
    """
    return x.replace("\n    ", "\n")


def local_string_toString():
    x = """
    def __ee_extra_string_toString(string):
        vars_name = varName(string)
        if isinstance(string, int):
            return str(string)
        elif isinstance(string, str):
            return str(string)
        elif isinstance(string, list):
            return ", ".join([str(xchr) for xchr in string])
        return eval("%s.toString()" % vars_name)    
    """
    return x.replace("\n    ", "\n")


def local_string_trim():
    x = """
    def __ee_extra_string_trim(string):
        vars_name = varName(string)
        if isinstance(string, str):
            return string.strip()
        return eval("%s.trim()" % vars_name)
    """
    return x.replace("\n    ", "\n")


def translate_string(x):
    """Translates Javascript string methods to Python
    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_string
        >>> translate_string(x = '"LesLywashere".substring(1,3)')
    """
    eextra_special_functions_to = []
    specialfun_counter = 0

    # 0. Returns the Unicode of the character at the specified index in a string
    x, cond = translate_string_charCodeAt(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(local_string_charCodeAt())

    # 1. Remove whitespace from the beginning and end of the string.
    x, cond = translate_string_trim(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(local_string_trim())

    # 2. Searches a string for a match against a regular expression, and returns the matches.
    x, cond = translate_string_match(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(local_string_match())

    # 3. Extracts a part of a string and returns a new string.
    x, cond = translate_string_slice(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(local_string_slice())

    # 4. Extracts the characters from a string, beginning at a specified
    # start position, and through the specified number of character.
    x, cond = translate_string_substr(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(local_string_substr())

    # 5. Searches a string for a specified value, or regular expression,
    # and returns the position of the match.
    x, cond = translate_string_search(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(local_string_search())

    # 6. Returns the character at the specified index (position) of a string.
    x, cond = translate_string_charAt(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(local_string_charAt())

    # 7. Joins two or more strings, and returns a new joined strings.
    x, cond = translate_string_concat(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(local_string_concat())

    # 8. Returns the length of a string.
    x, cond = translate_string_length(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(local_string_length())

    # 9. Returns the value of a String object.
    x, cond = translate_string_toString(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(local_string_toString())

    # 10. Returns the position of the first found occurrence of a
    # specified value in a string.
    x, cond = translate_string_indexOf(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(local_string_indexOf())

    # 11. Extracts the characters from a string, between two
    # specified indices.
    x, cond = translate_string_substring(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(local_string_substring())

    # 12. Returns the position of the last found occurrence of
    # a specified value in a string.
    x, cond = translate_string_lastIndexOf(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(local_string_lastIndexOf())

    # 13. Converts a string to uppercase letters
    x, cond = translate_string_toUpperCase(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(local_string_toUpperCase())

    # 14. Compares two strings in the current locale
    x, cond = translate_string_localeCompare(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(local_string_localeCompare())

    # 15. Converts a string to lowercase letters
    x, cond = translate_string_toLowerCase(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(local_string_toLowerCase())

    # If a special function is found, return varname func too
    if specialfun_counter > 0:
        eextra_special_functions_to.append(local_string_varname())

    return x, "\n".join(eextra_special_functions_to)
