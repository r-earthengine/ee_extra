import regex


# Wrapper functions to translate all functions --------------------------------
def functextin(x, fname="parseInt"):
    """Get the body of a function.

    Args:
        x (str): JavaScript code to translate.
        fname (str, optional): Name of the function. Defaults to "parseInt".

    Returns:
        str: Body of the function.

    Examples:
        >>> from ee_extra import functextin
        >>> functextin('parseInt(a=2)')
    """

    search = "(?<![\w\.])%s\(" % fname
    matches = regex.finditer(search, x, regex.MULTILINE)
    paranthesis_index = list()
    for _, match in enumerate(matches):
        search_parenthesis = match.end()
        pnumber = 1
        counter = 0
        paranthesis_body = list()
        while pnumber > 0:
            if x[search_parenthesis + counter] == "(":
                pnumber += 1
            elif x[search_parenthesis + counter] == ")":
                pnumber -= 1
            paranthesis_body.append(x[search_parenthesis + counter])
            counter += 1
        paranthesis_index.append("".join(paranthesis_body[:-1]))
    return paranthesis_index


def translate_fun_parseInt(x):
    """Converts parseInt(string, radix) to
    __extrafunc_parseInt(string, radix=10)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_fun_parseInt
        >>> translate_fun_parseInt('1010101', 2)
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    arg_names = list(set(functextin(x, "parseInt")))

    # if does not match the condition, return the original string
    if arg_names == []:
        return x, 0

    replacement = [f"parseInt({arg_name})" for arg_name in arg_names]
    to_replace_by = [
        "__ee_extrafunc_parseInt(%s)" % (arg_name) for arg_name in arg_names
    ]

    # Replace string by our built-in function
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_fun_parseFloat(x):
    """Converts parseFloat(string) to
    __extrafunc_parseFloat(string)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_fun_parseFloat
        >>> translate_fun_parseFloat(x = "parseFloat(1010101)")
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    arg_names = list(set(functextin(x, "parseFloat")))

    # if does not match the condition, return the original string
    if arg_names == []:
        return x, 0

    replacement = [f"parseFloat({arg_name})" for arg_name in arg_names]
    to_replace_by = [
        "__ee_extrafunc_parseFloat(%s)" % (arg_name) for arg_name in arg_names
    ]

    # Replace string by our built-in function
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_fun_Number(x):
    """Converts Number(string) to
    __extrafunc_Number(string)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_fun_parseFloat
        >>> translate_fun_parseFloat(x = "Number('1010101')")
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    arg_names = list(set(functextin(x, "Number")))

    # if does not match the condition, return the original string
    if arg_names == []:
        return x, 0

    replacement = [f"Number({arg_name})" for arg_name in arg_names]
    to_replace_by = ["__ee_extrafunc_Number(%s)" % (arg_name) for arg_name in arg_names]

    # Replace string by our built-in function
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 1


def translate_fun_String(x):
    """Converts String(int|float) to
    __extrafunc_String(int|float)

    Args:
        x (str): JavaScript code to translate.

    Returns:
        str: Translated JavaScript code.

    Examples:
        >>> from ee_extra import translate_fun_String
        >>> translate_fun_String("String(224)")
    """
    # Regex conditions to get the string to replace,
    # the arguments, and the variable name.
    arg_names = list(set(functextin(x, "String")))

    # if does not match the condition, return the original string
    if arg_names == []:
        return x, 0

    replacement = [f"String({arg_name})" for arg_name in arg_names]
    to_replace_by = ["__ee_extrafunc_String(%s)" % (arg_name) for arg_name in arg_names]

    # Replace string by our built-in function
    for z in zip(replacement, to_replace_by):
        x = x.replace(z[0], z[1])
    return x, 0


# Funs to copy on the main file ------------------------------------------------
def local_fun_parseInt():
    x = """
    def __ee_extrafunc_parseInt(string, radix=10):
        vars_name = varName(string)
        if isinstance(string, str):
            return int(string, radix)
        return eval("%s.parseInt(%s)" % (vars_name, radix))
    """
    return x.replace("\n    ", "\n")


def local_fun_parseFloat():
    x = """
    def __ee_extrafunc_parseFloat(string):
        vars_name = varName(string)
        if isinstance(string, str):
            condition = r"([0-9]+)([a-zA-Z]+)"
            if regex.search(condition, string):
                string = regex.match(condition, string).group(1)
            return float(string)
        return eval("parseInt(%s)" % (vars_name))
    """
    return x.replace("\n    ", "\n")


def local_fun_Number():
    x = """
    def __ee_extrafunc_Number(string):
        vars_name = varName(string)
        if isinstance(string, str):
            return int(string)
        return eval("Number(%s)" % (vars_name))
    """
    return x.replace("\n    ", "\n")


def local_fun_String():
    x = """
    def __ee_extrafunc_String(string):
        return str(string)
    """
    return x.replace("\n    ", "\n")
