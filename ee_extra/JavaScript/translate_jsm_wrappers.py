import regex

from ee_extra.JavaScript.translate_utils import (
    search_after,
    search_after_attribute,
    search_before,
    search_open_parenthesis,
    search_open_square_bracket,
)


# -----------------------------------------------------------------------------
# Given:
# >>>> var lista = [1, 2, 3, 4];
# >>>> print(lista.concat([5, 6, 7, 8]));
#
# The functions fcondition01, fcondition02, and fcondition03 help
# to obtain the variable name (lista), the word to replace
# (lista.concat([5, 6, 7, 8]), and the arguments (5, 6, 7, 8).
def get_finditer_cases(condition, text):
    """
    get the results after apply a naive regex cond an the position of the
    point method.
    """
    results = list()
    results_position = list()
    for match in regex.finditer(condition, text):
        match_group = match.group(1)
        results.append(match_group)
        results_position.append(match.start() + len(match_group))
    return results, results_position


def fcondition01(line, method_name, attribute=False, extra=""):
    """Obtain the varname
    e.g.
        - lesly.every(checkAge) -> lesly
        - [1, 2, 3, 4].every(checkAge) -> [1, 2, 3, 4]
        - "cesar".every(checkAge) -> "cesar"
    """
    # Detect possible cases (just detect!)
    if not attribute:
        fcondition = "([\w'\"\]\)%s]+?)\.%s\((?>[^()]+|(?1))*\)" % (extra, method_name)
    else:
        fcondition = "([\w'\"\]\)%s]+?)\.%s" % (extra, method_name)

    results, results_position = get_finditer_cases(fcondition, line)

    # if is a attribute, delete cases with parenthesis.
    if attribute:
        new_result_positions = list()
        new_results = list()
        for xnew_result, position in zip(results, results_position):
            text_after = search_after_attribute(position=position, text=line)
            if ")" not in text_after:
                new_result_positions.append(position)
                new_results.append(xnew_result)
        results_position = new_result_positions
        results = new_results

    # if there is no cases skip it!
    if results == []:
        return []

    # supporting list inplace methods -> e.g. [1, 2, 3, 4].every(checkAge)
    new_results = list()
    for index, result in enumerate(results):
        if search_open_square_bracket(result):
            new_result = search_before(
                position=results_position[index], text=line, pattern=["[", "]"]
            )
            new_result = f"{new_result}]"
            # your [...] has commas? then is a list but
            # it is a subset of a list, i mean xxx[i]
            new_results.append(new_result)
        elif search_open_parenthesis(result):
            new_result = search_before(
                position=results_position[index], text=line, pattern=["(", ")"]
            )
            new_result = f"{new_result})"
            new_results.append(new_result)
        else:
            new_results.append(result)
    return new_results


def fcondition02(line, method_name="every", extra=""):
    """Obtain the word to replace
    e.g.
        - print(lesly.every(checkAge)) -> lesly.every(checkAge)
        - print([1, 2, 3, 4].every(checkAge)) -> [1, 2, 3, 4].every(checkAge)
        - ["cesar".every(checkAge)] -> "cesar".every(checkAge)
    """
    fcondition = "([\w'\"\]\)%s]+?)\.%s\((?>[^()]+|(?1))*\)" % (extra, method_name)
    results, results_position = get_finditer_cases(fcondition, line)
    variables = fcondition01(line, method_name=method_name, extra=extra)

    if results == []:
        return []

    # supporting list inplace methods -> e.g. [1, 2, 3, 4].every(checkAge)
    new_results = []
    for index, result in enumerate(results):
        new_result = search_after(position=results_position[index], text=line)
        new_result = "%s.%s" % (variables[index], new_result)
        new_results.append(new_result)
    return new_results


def fcondition03(line, method_name, extra=""):
    """Obtain the arguments
    e.g.
        - print(lesly.every(checkAge)) -> checkAge
        - print([1, 2, 3, 4].every(checkAge)) -> checkAge
        - ["cesar".every(checkAge)] -> checkAge
    """
    fcondition = "([\w'\"\]\)%s]+?)\.%s\((?>[^()]+|(?1))*\)" % (extra, method_name)
    results, results_position = get_finditer_cases(fcondition, line)
    variables = fcondition01(line, method_name=method_name, extra=extra)

    if results == []:
        return []

    # supporting list inplace methods -> e.g. [1, 2, 3, 4].every(checkAge)
    new_results = []
    for index, result in enumerate(results):
        new_result = search_after(position=results_position[index], text=line)
        new_result = new_result[new_result.find("(") :][1:-1]
        new_results.append(new_result)
    return new_results


# -----------------------------------------------------------------------------


def translate_charAt(x):
    """Converts string.charAt(index) to __ee_extra_charAt(string, index)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_charAt
        >>> translate_charAt(x = "'hello'.charAt(0)")
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.

    var_names = fcondition01(x, "charAt")
    replacement = fcondition02(x, "charAt")
    arg_names = fcondition03(x, "charAt")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_charAt(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_concat(x):
    """Converts string.concat(string1, string2, ...) to
    __ee_extra_concat(string, string1, string2, ...)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_concat
        >>> translate_concat("'hello'.concat('world', 'lalesly')")
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "concat")
    replacement = fcondition02(x, "concat")
    arg_names = fcondition03(x, "concat")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_concat(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_indexOf(x):
    """Converts string.indexOf(string) to __ee_extra_indexOf(string, string)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_concat
        >>> translate_concat("'hello'.concat('world', 'lalesly')")
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "indexOf")
    replacement = fcondition02(x, "indexOf")
    arg_names = fcondition03(x, "indexOf")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_indexOf(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_lastIndexOf(x):
    """Converts string.lastIndexOf(string) to
    __ee_extra_lastIndexOf(string, string)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_lastIndexOf
        >>> translate_lastIndexOf("'daniel'.lastIndexOf('s')")
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "lastIndexOf")
    replacement = fcondition02(x, "lastIndexOf")
    arg_names = fcondition03(x, "lastIndexOf")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_lastIndexOf(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_localeCompare(x):
    """Converts string.localeCompare(compareString) to
    __ee_extra_localeCompare(string, compareString)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_localeCompare
        >>> translate_localeCompare('"hi".localeCompare("s")')
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "localeCompare")
    replacement = fcondition02(x, "localeCompare")
    arg_names = fcondition03(x, "localeCompare")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_localeCompare(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_length(x):
    """Converts string.length to __ee_extra_length(string)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_length
        >>> translate_length('myfuc(lesly.length, 10)')
    """

    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "length", attribute=True)
    replacement = [var_name + ".length" for var_name in var_names]

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = ["__ee_extra_length(%s)" % var_name for var_name in var_names]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_match(x):
    """Converts string.match(regexp) to __ee_extra_match(string, regexp)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_match
        >>> translate_match(x = '"hi".match("h")')
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "match")
    replacement = fcondition02(x, "match")
    arg_names = fcondition03(x, "match")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_match(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_search(x):
    """Converts string.search(regexp) to __ee_extra_search(string, regexp)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_search
        >>> translate_search(x = '"hi".search("h")')
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "search")
    replacement = fcondition02(x, "search")
    arg_names = fcondition03(x, "search")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_search(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_slice(x):
    """Converts string.slice(start, end) to __ee_extra_slice(string, start, end)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_slice
        >>> translate_slice(x = '"hilesly".slice(1,3)')
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "slice")
    replacement = fcondition02(x, "slice")
    arg_names = fcondition03(x, "slice")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_slice(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_substr(x):
    """Converts string.substr(start, length)
    to __ee_extra_substr(string, start, length)
    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_substr
        >>> translate_substr(x = '"leslywashere".substr(2, 4)')
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "substr")
    replacement = fcondition02(x, "substr")
    arg_names = fcondition03(x, "substr")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_substr(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_substring(x):
    """Converts string.substring(start, length)
    to __ee_extra_substring(string, start, length)
    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_substring
        >>> translate_substring(x = '"leslywashere".substring(2, 4)')
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "substring")
    replacement = fcondition02(x, "substring")
    arg_names = fcondition03(x, "substring")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_substring(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_toLowerCase(x):
    """Converts string.toLowerCase() to __ee_extra_toLowerCase(string)
    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_toLowerCase
        >>> translate_toLowerCase(x = '"LesLywashere".toLowerCase()')
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "toLowerCase")
    replacement = fcondition02(x, "toLowerCase")
    arg_names = fcondition03(x, "toLowerCase")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_toLowerCase(%s)" % (var_name) for var_name in var_names
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_toLocaleLowerCase(x):
    """Converts string.toLocaleLowerCase() to __ee_extra_toLowerCase(string)
    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_toLocaleLowerCase
        >>> translate_toLocaleLowerCase(x = '"LesLywashere".toLocaleLowerCase()')
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "toLocaleLowerCase")
    replacement = fcondition02(x, "toLocaleLowerCase")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_toLowerCase(%s)" % (var_name) for var_name in var_names
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_toUpperCase(x):
    """Converts string.toUpperCase() to __ee_extra_toUpperCase(string)
    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_toUpperCase
        >>> translate_toUpperCase(x = '"LesLywashere".toUpperCase()')
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "toUpperCase")
    replacement = fcondition02(x, "toUpperCase")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_toUpperCase(%s)" % (var_name) for var_name in var_names
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_toLocaleUpperCase(x):
    """Converts string.toLocaleUpperCase() to __ee_extra_toUpperCase(string)
    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_toLocaleUpperCase
        >>> translate_toLocaleUpperCase(x = '"LesLywashere".toLocaleUpperCase()')
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "toLocaleUpperCase")
    replacement = fcondition02(x, "toLocaleUpperCase")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_toUpperCase(%s)" % (var_name) for var_name in var_names
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_toString(x):
    """Converts string.toString() to __ee_extra_toString(string)
    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_toString
        >>> translate_toString(x = 'var lesly=10\nlesly.toString()')
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "toString")
    replacement = fcondition02(x, "toString")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = ["__ee_extra_toString(%s)" % (var_name) for var_name in var_names]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_trim(x):
    """Converts string.trim() to __ee_extra_trim(string)
    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_trim
        >>> translate_trim(x = "var lesly=' lesly  '.trim()")
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "trim", extra="\s")
    replacement = fcondition02(x, "trim", extra="\s")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = ["__ee_extra_trim(%s)" % (var_name) for var_name in var_names]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_charCodeAt(x):
    """Converts string.charCodeAt(index) to __ee_extra_charCodeAt(string, index)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_charCodeAt
        >>> translate_charCodeAt(x="'hello'.charCodeAt(0)")
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "charCodeAt")
    replacement = fcondition02(x, "charCodeAt")
    arg_names = fcondition03(x, "charCodeAt")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_charCodeAt(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_every(x):
    """Converts list.every(function, thisValue) to __ee_extra_every(function, thisValue)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_every
        >>> text = "var ages = [32, 33, 16, 40]\n" +\
        >>>        "ages.every(function(age) { return age >= 18; });\n" +\
        >>>        "ages.every(checkAge)"
        >>> translate_every(text)
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "every")
    replacement = fcondition02(x, "every")
    arg_names = fcondition03(x, "every")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_every(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_filter(x):
    """Converts list.filter(function, thisValue) to __ee_extra_filter(function, thisValue)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_filter
        >>> text = "var ages = [32, 33, 16, 40]\n" +\
        >>>        "ages.every(function(age) { return age >= 18; });\n" +\
        >>>        "ages.every(checkAge)"
        >>> translate_filter(text)
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "filter")
    replacement = fcondition02(x, "filter")
    arg_names = fcondition03(x, "filter")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_filter(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_foreach(x):
    """Converts list.foreach(function) to __ee_extra_foreach(function, list)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_foreach
        >>> text = "var text = "";\nvar fruits = ["apple", "orange", "cherry"];\n" +\
        >>>        "function demo(item, index) {text += index + ": " + item + "<br>";};\n" +\
        >>>        "fruits.forEach(demo)"
        >>> translate_foreach(text)
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "forEach")
    replacement = fcondition02(x, "forEach")
    arg_names = fcondition03(x, "forEach")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_foreach(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_arrayfrom(x):
    """Converts Array.from(iterable) to __ee_extra_arrayfrom(iterable)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_foreach
        >>> text = 'print(Array.from("ABCDEFG"))'
        >>> translate_foreach(text)
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "from")
    replacement = fcondition02(x, "from")
    arg_names = fcondition03(x, "from")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_arrayfrom(%s)" % (arg_name)
        for arg_name, _ in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_isArray(x):
    """Converts Array.isArray(list) to __ee_extra_isArray(list)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_isArray
        >>> text = 'Array.isArray(["Banana", "Orange", "Apple", "Mango"])'
        >>> translate_isArray(text)
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "isArray")
    replacement = fcondition02(x, "isArray")
    arg_names = fcondition03(x, "isArray")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_isArray(%s)" % (arg_name)
        for arg_name, _ in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_join(x):
    """Converts list.join(separator) to __ee_extra_isArray(list, separator)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_join
        >>> text = '["Banana", "Orange", "Apple", "Mango"].join("d")'
        >>> translate_join(text)
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "join")
    replacement = fcondition02(x, "join")
    arg_names = fcondition03(x, "join")
    if arg_names == [""]:
        arg_names = ['","']

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_join(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_map(x):
    """Converts list.map(function) to __ee_extra_map(list, function)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_map
        >>> text = '[4, 9, 16, 25].map(Math.sqrt)'
        >>> translate_map(newArr)
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "map")
    replacement = fcondition02(x, "map")
    arg_names = fcondition03(x, "map")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_map(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_push(x):
    """Converts list.push(v1, v2, ....) to __ee_extra_push(list, v1, v2, ...)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_push
        >>> text = '["Banana", "Orange", "Apple", "Mango"].push("Kiwi", "Pera")'
        >>> translate_map(newArr)
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "push")
    replacement = fcondition02(x, "push")
    arg_names = fcondition03(x, "push")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_push(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_reduce(x):
    """Converts list.reduce(function) to __ee_extra_reduce(list, function)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_reduce
        >>> text = 'var nn = [15.5, 2.3, 1.1, 4.7]\n' +\
                   'function myFunc(total, num) { return total - num}\n' +\
                   'print(nn.reduce(myFunc))'
        >>> translate_reduce(text)
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "reduce")
    replacement = fcondition02(x, "reduce")
    arg_names = fcondition03(x, "reduce")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_reduce(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_reduceRight(x):
    """Converts list.reduceRight(function) to __ee_extra_reduceRight(list, function)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_reduceRight
        >>> text = 'var nn = [15.5, 2.3, 1.1, 4.7]\n' +\
                   'function myFunc(total, num) { return total - num}\n' +\
                   'print(nn.reduceRight(myFunc))'
        >>> translate_reduceRight(text)
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "reduceRight")
    replacement = fcondition02(x, "reduceRight")
    arg_names = fcondition03(x, "reduceRight")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_reduceRight(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_shift(x):
    """Converts list.shift() to __ee_extra_shift(list)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_shift
        >>> text = 'var nn = [15.5, 2.3, 1.1, 4.7]\n' +\
                   'nn.shift()\n' +\
                   'print(nn)'
        >>> translate_shift(text)
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "shift")
    replacement = fcondition02(x, "shift")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = ["__ee_extra_shift(%s)" % (var_name) for var_name in var_names]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_some(x):
    """Converts list.some(function) to __ee_extra_some(list, function)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_some
        >>> text = 'var nn = [15.5, 2.3, 1.1, 4.7]\n' +\
                   'function checkAdult(age) {return age >= 18}\n' +\
                   'print(ages.some(checkAdult))'
        >>> translate_some(text)
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "some")
    replacement = fcondition02(x, "some")
    arg_names = fcondition03(x, "some")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_some(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_splice(x):
    """Converts list.splice(index, howmany, item1, ... itemx) to 
       __ee_extra_splice(list, index, howmany, item1, ... itemx)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_splice
        >>> text = 'var fruits = ["Banana", "Orange", "Apple", "Mango"];\n' +\
                   'fruits.splice(2, 1)'
        >>> translate_splice(text)
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "splice")
    replacement = fcondition02(x, "splice")
    arg_names = fcondition03(x, "splice")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_splice(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_unshift(x):
    """Converts list.unshift(item1, item2, ..., itemX) to
       __ee_extra_unshift(list, item1, item2, ..., itemX)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_unshift
        >>> text = '["Banana", "Orange", "Apple", "Mango"].unshift("Lemon","Pineapple")'
        >>> translate_unshift(text)
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "unshift")
    replacement = fcondition02(x, "unshift")
    arg_names = fcondition03(x, "unshift")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_unshift(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_valueOf(x):
    """Converts list.valueOf() to __ee_extra_valueOf(list)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_valueOf
        >>> text = '["Banana", "Orange", "Apple", "Mango"].valueOf()'
        >>> translate_valueOf(text)
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    var_names = fcondition01(x, "valueOf")
    replacement = fcondition02(x, "valueOf")
    arg_names = fcondition03(x, "valueOf")

    # if does not match the condition, return the original string
    if var_names == []:
        return x, 0

    # Replace string by our built-in function
    to_replace_by = [
        "__ee_extra_valueOf(%s, %s)" % (var_name, arg_name)
        for arg_name, var_name in zip(arg_names, var_names)
    ]
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1
