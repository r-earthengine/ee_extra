from ee_extra import translate_jsm_extra as jsmextra
from ee_extra import translate_jsm_wrappers as jsmwrappers
from ee_extra import translate_specialfunctions as fspecial

def translate_jsmethods(x):
    """Translates Javascript methods to Python
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
    x, cond = jsmwrappers.translate_charCodeAt(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_charCodeAt())

    # 1. Remove whitespace from the beginning and end of the string.
    x, cond = jsmwrappers.translate_trim(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_trim())

    # 2. Searches a string for a match against a regular expression, and returns the matches.
    x, cond = jsmwrappers.translate_match(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_match())

    # 3. Extracts a part of a string and returns a new string.
    x, cond = jsmwrappers.translate_slice(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_slice())

    # 4. Extracts the characters from a string, beginning at a specified
    # start position, and through the specified number of character.
    x, cond = jsmwrappers.translate_substr(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_substr())

    # 5. Searches a string for a specified value, or regular expression,
    # and returns the position of the match.
    x, cond = jsmwrappers.translate_search(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_search())

    # 6. Returns the character at the specified index (position) of a string.
    x, cond = jsmwrappers.translate_charAt(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_charAt())

    # 7. Joins two or more strings, and returns a new joined strings.
    x, cond = jsmwrappers.translate_concat(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_concat())

    # 8. Returns the length of a string.
    x, cond = jsmwrappers.translate_length(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_length())

    # 9. Returns the value of a String object.
    x, cond = jsmwrappers.translate_toString(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_toString())

    # 10. Returns the position of the first found occurrence of a
    # specified value in a string.
    x, cond = jsmwrappers.translate_indexOf(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_indexOf())

    # 11. Extracts the characters from a string, between two
    # specified indices.
    x, cond = jsmwrappers.translate_substring(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_substring())

    # 12. Returns the position of the last found occurrence of
    # a specified value in a string.
    x, cond = jsmwrappers.translate_lastIndexOf(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_lastIndexOf())

    # 13. Converts a string to uppercase letters
    x, cond = jsmwrappers.translate_toUpperCase(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_toUpperCase())

    # 14. Compares two strings in the current locale
    x, cond = jsmwrappers.translate_localeCompare(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_localeCompare())

    # 15. Converts a string to lowercase letters
    x, cond = jsmwrappers.translate_toLowerCase(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_toLowerCase())

    # Returns true if all elements in an array pass a test (provided as a function).
    x, cond = jsmwrappers.translate_every(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_every())

    # Returns true if all elements in an array pass a test (provided as a function).
    x, cond = jsmwrappers.translate_filter(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_filter())

    # Returns true if all elements in an array pass a test (provided as a function).
    x, cond = jsmwrappers.translate_foreach(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_foreach())

    # Returns true if all elements in an array pass a test (provided as a function).
    x, cond = jsmwrappers.translate_arrayfrom(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_arrayfrom())

    # Returns true if x is a list.
    x, cond = jsmwrappers.translate_isArray(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_isArray())

    # join method returns an array as a string.
    x, cond = jsmwrappers.translate_join(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_join())

    # Creates a new array with the results of calling a function for every array element.
    x, cond = jsmwrappers.translate_map(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_map())

    # The push method adds new items to the end of an array.
    x, cond = jsmwrappers.translate_push(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_push())

    # reducer function for each value of an array , from left to right.
    x, cond = jsmwrappers.translate_reduce(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_reduce())

    # reducer function for each value of an array , from right to left
    x, cond = jsmwrappers.translate_reduceRight(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_reduceRight())

    # Remove the first element of an array and returns that element.
    x, cond = jsmwrappers.translate_shift(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_shift())

    # Remove the first element of an array and returns that element.
    x, cond = jsmwrappers.translate_some(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_some())

    # Add elements to an array.
    x, cond = jsmwrappers.translate_splice(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_splice())

    # Add new items to the beginning of an array.
    x, cond = jsmwrappers.translate_unshift(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_unshift())

    # valueOf() is the default method of any Array object... aparently does not do nothing.
    x, cond = jsmwrappers.translate_valueOf(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(jsmextra.local_valueOf())

    x, cond = fspecial.translate_fun_parseInt(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(fspecial.local_fun_parseInt())

    x, cond = fspecial.translate_fun_parseFloat(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(fspecial.local_fun_parseFloat())

    x, cond = fspecial.translate_fun_Number(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(fspecial.local_fun_Number())

    x, cond = fspecial.translate_fun_String(x)
    if cond:
        specialfun_counter += 1
        eextra_special_functions_to.append(fspecial.local_fun_String())

    # ---------------------------------------------------------------
    # If a special function is found, return varname func too
    # ---------------------------------------------------------------
    if specialfun_counter > 0:
        eextra_special_functions_to.append(jsmextra.local_varname())

    return x, "\n".join(eextra_special_functions_to)
