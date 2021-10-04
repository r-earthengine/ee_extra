""" Functions used in 'utils.py', 'utils_general.py', and 'utils_loops.py'."""
from itertools import islice, zip_longest
import regex
import keyword


def from_bin_to_list(x):
    """Helper function to group lines

    Args:
        x (str): A binary string where 1 represents a line on the file that must be subgrouped.

    Returns:
        [list]: A list with the index of the lines to aggreggate.

    Example:
        >>> from ee_extra import from_bin_to_list
        >>> from_bin_to_list("001110101")
        >>> # [0, 1, [2, 3, 4], 5, [6], 7, [8]]
    """
    group_list = list(yield_subgroups(x, subgroup_test=lambda i, j: i + j))[1:]
    list_01 = []
    counter = 0
    for value2 in group_list:
        # all are zero?
        value2 = [int(i) for i in value2]
        if sum(value2) == 0:
            for _ in value2:
                list_01.append(counter)
                counter += 1
        else:
            value2 = [value + counter for value in range(len(value2))]
            list_01.append(value2)
            counter = value2[-1] + 1
    return list_01


def yield_subgroups(group, subgroup_test):
    """ Helper function to group lines see from_bin_to_list"""
    subgroup = [0]
    for i, j in zip_longest(group, islice(group, 1, None), fillvalue=0):
        if subgroup_test(str(i), str(j)) in ["00", "01"]:
            if subgroup[-1] == "0":
                subgroup.append(i)
            else:
                yield subgroup
                subgroup = [i]
        else:
            if subgroup[-1] == "1":
                subgroup.append(i)
            else:
                yield subgroup
                subgroup = [i]
    yield subgroup


def var_remove(x):
    """Remove reserved keyword 'var'

    var cesar = 10 --> cesar = 10

    Args:
        x (str): A string with Javascript syntax.

    Returns:
        [str]: Python string

    Examples:
        >>> from ee_extra import var_remove
        >>> var_remove("var cesar = 10")
        >>> # cesar = 10
    """
    pattern = r"var(.*?)="
    matches = regex.findall(pattern, x, regex.DOTALL)
    var_names = [regex.sub("\s+", "", match) for match in matches]

    if set(var_names) & set(keyword.kwlist) != set():
        raise NameError(
            "ee_extra can not assign a value to a Python reserved keyword: ",
            "var_names: %s" % " ,".join(var_names),
        )

    if not matches == []:
        for match in matches:
            x = x.replace(f"var{match}=", f"{match.replace(' ','')} =")
    return x


def delete_brackets(x):
    """Remove excess of curly braces

    obj={'b':'a'}} --> obj={'b':'a'}

    Args:
        x (str): A string with Javascript syntax.

    Returns:
        [str]: Python string

    Examples:
        >>> from ee_extra import delete_brackets
        >>> delete_brackets("obj={'b':'a'}}")
        >>> # obj={'b':'a'}
    """
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
