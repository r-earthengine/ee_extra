"""
Auxiliary module with functions to translate JavaScript loops to Python.

In GEE JavaScript there is four diferent ways to define a loop:

    1. JS loop FOR.
    2. JS loop FOR IN.    
    3. JS loop WHILE.
    4. JS loop SWITCH.

This module try to convert all theses cases to Python. If you consider that
there is more cases that must be added to the module, please, contact us by
GitHub :).
"""
import regex
from ee_extra import from_bin_to_list, var_remove, delete_brackets


def fix_case03_loop(x):
    """Standarize for loop styles.

    for(_) \n ... -> for(_) ...

    Args:
        x (str): A string with Javascript syntax.

    Returns:
        [str]: Python string

    Examples:
        >>> from ee_extra import fix_case03_loop
        >>> fix_case03_loop('for (var i = 0; i < 5; i++) \n numbers[i]')
        >>> # 'for (var i = 0; i < 5; i++) numbers[i]'
    """
    lines = x.split("\n")
    fulfill_condition = list()
    merge_condition = list("0" * len(lines))

    # Is a line with a for loop?
    for line in lines:
        # 1. Get the text inside parenthesis (ignore nested parenthesis)
        condition_01 = "(?<=for\s*\()(?:[^()]+|\([^)]+\))+(?=\))"
        matches = list(regex.finditer(condition_01, line))
        if matches == []:
            fulfill_condition.append(False)
        else:
            fulfill_condition.append(True)

    # Check if the for loop lines meet the condition "case03"
    lines_to_check = [lines[index] for index, x in enumerate(fulfill_condition) if x]
    index01 = [index for index, x in enumerate(fulfill_condition) if x]

    def fast_ck03(line):
        return regex.findall("\).*", line)[0][1:].strip() == ""

    index02 = [index for index, x in enumerate(lines_to_check) if fast_ck03(x)]
    index03 = [index01[x] for x in index02]

    # Create the merge condition and the merge subgroups
    for index in index03:
        merge_condition[index] = "1"
    subgroups = "".join(merge_condition)
    subgroups = subgroups.replace("10", "11")
    merge_rule = from_bin_to_list(subgroups)

    # Create the new x string
    final_x = list()
    for index in merge_rule:
        if isinstance(index, list):
            final_x.append("".join([lines[index2] for index2 in index]))
        else:
            final_x.append(lines[index])
    return "\n".join(final_x)


def fix_while_loop(x):
    """Change Javascript for loop to Python for loop

    for(var i = 0fi < x.length;i++){" --> "for i in range(0,len(x),1):

    Args:
        x (str): A string with Javascript syntax.

    Returns:
        [str]: Python string

    Examples:
        >>> from ee_extra import fix_for_loop
        >>> fix_for_loop('for(var i = 0;i < x.length;i++){\nprint(i)\n}')
        >>> # var x = ee.Image(0)
    """
    # Fix the case03 loop style (See bellow)
    x = fix_case03_loop(x)
    lines = x.split("\n")
    list_while_solver = list()

    # line = lines[4]
    for line in lines:
        # 1. Get the text inside parenthesis (ignore nested parenthesis)
        condition_01 = "(?<=while.*\()(?:[^()]+|\([^)]+\))+(?=\))"
        matches = list(regex.finditer(condition_01, line))
        initial_white_space = regex.findall("^\s*", line)[0]
        if matches == []:
            list_while_solver.append(line)
            continue
        for match in matches:
            while_loop_body = match.group()  # get the match
        python_while_loop = "while %s:" % while_loop_body.replace("var ", "")

        # This chunk of code support three different ways for defining a loop
        # (there is just 3 types because beautify reformat perfectly the code!)
        # while(_) \n { \n ... --> case01
        # while(_) ...         --> case02
        # while(_) \n ...      --> case03

        # what is there after closing the parenthesis?
        while_condition = regex.findall("\).*", line)[0][1:].strip()
        python_while_loop = initial_white_space + python_while_loop + "\n"
        # Case 01
        if while_condition == "{":
            list_while_solver.append(python_while_loop)
        # Case 02
        else:
            list_while_solver.append("%s    %s" % (python_while_loop, while_condition))
    return "\n".join(list_while_solver)


def fix_for_loop(x):
    """Change Javascript for loop to Python for loop

    for(var i = 0fi < x.length;i++){" --> "for i in range(0,len(x),1):

    Args:
        x (str): A string with Javascript syntax.

    Returns:
        [str]: Python string

    Examples:
        >>> from ee_extra import fix_for_loop
        >>> fix_for_loop('for(var i = 0;i < x.length;i++){\nprint(i)\n}')
        >>> # var x = ee.Image(0)
    """
    # Fix the case03 loop style (See bellow)
    x = fix_case03_loop(x)

    lines = x.split("\n")

    list_for_solver = list()
    
    # line = lines[4]    
    for line in lines:
        # 1. Get the text inside parenthesis (ignore nested parenthesis)
        condition_01 = "(?<=for\s*\()(?:[^()]+|\([^)]+\))+(?=\))"
        matches = list(regex.finditer(condition_01, line))
        if matches == []:
            list_for_solver.append(line)
            continue                
        # get the text inside for loop parenthesis
        for match in matches:
            for_loop_body = match.group()

        # initial space
        initial_white_space = regex.findall("^\s*", line)[0]
        
        
        ## Match for in
        if " in " in for_loop_body:
            python_for_loop = "for %s:" % for_loop_body.replace("var ", "")
        
        ## if the condition below is true, it means that the argument is True.
        if for_loop_body.split(";")[0] == for_loop_body:
            python_for_loop = "for %s:" % for_loop_body
        else:
            # 2. Get the groups
            for_loop_vars = for_loop_body.split(";")

            # 3. For loop operators
            cops = ["<=", "<", ">", ">=", "==", "!="]
            gradient = ["++", "--"]

            # 4. Get the definitions, the condition and the iterator
            lgradient = [
                for_loop_var
                for for_loop_var in for_loop_vars
                if any([cop in for_loop_var for cop in gradient])
            ]
            lcond = [
                for_loop_var
                for for_loop_var in for_loop_vars
                if any([cop in for_loop_var for cop in cops])
            ]
            ldef = [
                for_loop_var
                for for_loop_var in for_loop_vars
                if not for_loop_var in (lgradient + lcond)
            ]

            lcond = regex.sub("\s+", "", lcond[0])

            # 5. Get the iterator name and range
            fcop = [cop for cop in cops if cop in lcond][0]
            iterator = lcond.split(fcop)[0]

            # this statement is to transform the case of "for(;i < x.length;){...}" to while(i < x.length){...}
            if len(lgradient) == 0:
                ldef = "\n".join([regex.sub("\s+", "", var_remove(ld)) for ld in ldef])
                ldef = "\n".join(ldef.split(","))
                python_for_loop = delete_brackets(x="%s\nwhile %s :\n" % (ldef, lcond))
            else:
                lgradient = regex.sub("\s+", "", lgradient[0])
                ldef = "\n".join([regex.sub("\s+", "", var_remove(ld)) for ld in ldef])
                ldef = "\n".join(ldef.split(","))

                # 6. Get the step value
                if "++" in lgradient:
                    step = 1
                elif "--" in lgradient:
                    step = -1
                elif "+=" in lgradient:
                    step = lgradient.split("+=")[1]
                elif "-=" in lgradient:
                    step = lgradient.split("-=")[1]
                    step = f"-{step}"

                # 7. Get the start and stop values
                if fcop == "<=":
                    start = lcond.split("<=")[0]
                    stop = "(%s + 1)" % lcond.split("<=")[1]
                elif fcop == "<":
                    start = lcond.split("<")[0]
                    stop = lcond.split("<")[1]
                elif fcop == ">":
                    start = lcond.split(">")[1]
                    stop = lcond.split(">")[0]
                elif fcop == ">=":
                    start = lcond.split(">=")[1]
                    stop = "(%s + 1)" % lcond.split(">=")[0]
                elif fcop == "==":
                    start = lcond.split("==")[0]
                    stop = lcond.split("==")[1]
                elif fcop == "!=":
                    start = lcond.split("!=")[0]
                    stop = lcond.split("!=")[1]

                python_for_loop = delete_brackets(
                    x="%s\nfor %s in range(%s, %s, %s):\n"
                    % (ldef, iterator, start, stop, step)
                )

        # This chunk of code support three different ways for defining a loop
        # (there is just 3 types because beautify reformat perfectly the code!)
        # for(_) \n { \n ... --> case01
        # for(_) ...         --> case02
        # for(_) \n ...      --> case03

        # what is there after closing the parenthesis?
        for_condition = regex.findall("\).*", line)[0][1:].strip()
        python_for_loop = initial_white_space + python_for_loop
        # Case 01
        if for_condition == "{":
            list_for_solver.append(python_for_loop)
        # Case 02
        else:
            list_for_solver.append("%s    %s" % (python_for_loop, for_condition))
    return "\n".join(list_for_solver)


def fix_inline_iterators(x):
    """Fix inline iterators

    var i++; --> var i = i + 1;
    var --i; --> var i = i - 1;
    var i += 4; --> var i = i + 4;

    Args:
        x (str): A string with Javascript syntax.

    Returns:
        [str]: Python string

    Examples:
        >>> from ee_extra import fix_inline_iterators
        >>> fix_inline_iterators('++i;\ni+=4;')
        >>> # 'i = i + 1\ni = i + 4'
    """
    lines = x.split("\n")
    to_change = search_iterator(lines, 0)
    for index, ops in to_change:
        line = var_remove(lines[index])
        if ops == "++":
            varname = line.replace("++", "").replace(";", "")
            lines[index] = "%s = %s + 1" % (varname, varname)
        elif ops == "--":
            varname = line.replace("--", "").replace(";", "")

            lines[index] = "%s = %s - 1" % (varname, varname)
        elif ops == "+=":
            varname, counter = line.replace(";", "").split("+=")
            lines[index] = "%s = %s + %s" % (varname, varname, counter)
        elif ops == "-=":
            varname, counter = line.replace(";", "").split("-=")
            lines[index] = "%s = %s - %s" % (varname, varname, counter)
    return "\n".join(lines)


def search_iterator(lines, start=0):
    """Search for iterators in the code

    Args:
        lines ([list]): A list with Javascript syntax as strings.
        start ([int, optional]): The start line to start to search by iterators. Defaults to 0.

    Returns:
        [list]: A list of tuple (index, operator)
    """
    save_lines = list()
    iterator_ops = ["--", "++", "+=", "-="]
    for iterator_op in iterator_ops:
        for index in range(start, len(lines)):
            if iterator_op in lines[index]:
                save_lines.append((index, iterator_op))
    return save_lines
