""" Functions to support JavaScript methods 

** ___ee_extra_charCodeAt(string, index)
** ___ee_extra_charAt(string, index)
** ___ee_extra_concat(string, *args)
** ___ee_extra_indexOf(string, start)
** ___ee_extra_lastIndexOf(string, start)
** ___ee_extra_localeCompare(string, compareString)
** ___ee_extra_length(string) [string, list]
** ___ee_extra_match(string, regexp)
** ___ee_extra_search(string, regexp)
** ___ee_extra_slice(string, *args)
** ___ee_extra_substr(string, start, length)
** ___ee_extra_substring(string, start, end)
** ___ee_extra_toLowerCase(string)
** ___ee_extra_toUpperCase(string)
** ___ee_extra_trim(string)
** ___ee_extra_toString(string)
"""

# Local functions to add to the final script
def local_charCodeAt():
    x = """
    def __ee_extra_charCodeAt(string, index):
        vars_name = varName(string)
        if isinstance(string, str):
            return ord(string[index])
        return eval("%s.charAt(%s)" % (vars_name, index))
    """
    return x.replace("\n    ", "\n")


def local_varname():
    x = """
    def varName(var):
        lcls = inspect.stack()[2][0].f_locals
        for name in lcls:
            if id(var) == id(lcls[name]):
                return name
        return None
    """
    return x.replace("\n    ", "\n")


def local_charAt():
    x = """
    def __ee_extra_charAt(string, index):
        vars_name = varName(string)
        if isinstance(string, str):
            return string[index]
        return eval("%s.charAt(%s)" % (vars_name, index))
    """
    return x.replace("\n    ", "\n")


def local_concat():
    x = """
    def flatten(L):
        for item in L:
            try:
                yield from flatten(item)
            except TypeError:
                yield item
    
    def __ee_extra_concat(string, *args):
        vars_name = varName(string)
        if isinstance(string, str):
            return string + "".join(args)
        if isinstance(string, list):
            if isinstance(args, (list, tuple)):
                args_flatten = list(flatten(args))
                return string + args_flatten
            else:
                string.append(args)
                return string
        args = [str(arg)for arg in args]
        return eval("%s.concat(%s)" % (vars_name, ", ".join(args)))
    """
    return x.replace("\n    ", "\n")


def local_indexOf():
    x = """
    def __ee_extra_indexOf(iterable, start=None, item=None):
        vars_name = varName(iterable)
        if isinstance(iterable, str):
            search_string = regex.search(start, iterable)
            if search_string is None:
                return -1
            return search_string.start()
        elif isinstance(iterable, list):
            item, start = start, item
            if start is None:
                start = 0
            try:
                indexof = iterable.index(item, start)
            except:
                indexof=-1
            return indexof
        if item is None:
            return eval("%s.indexOf(%s, %s)" % (vars_name, start))
        else:
            return eval("%s.indexOf(%s, %s)" % (vars_name, item, start))
    """
    return x.replace("\n    ", "\n")


def local_lastIndexOf():
    x = """
    def __ee_extra_lastIndexOf(iterable, start=None, item=None):
        vars_name = varName(iterable)
        if isinstance(iterable, str):
            search_string = regex.search(start, iterable[::-1])
            if search_string is None:
                return -1
            return len(iterable) - search_string.start() - 1
        if isinstance(iterable, list):
            item, start = start, item
            if start is None:
                start = len(iterable) - 1            
            nstart = len(iterable) - start - 1
            return len(iterable) - 1 - iterable[::-1].index(item, nstart)
        return eval("%s.lastIndexOf(%s)" % (vars_name, start))
    """
    return x.replace("\n    ", "\n")


def local_localeCompare():
    x = """
    def __ee_extra_localeCompare(string, compareString):
        vars_name = varName(string)
        if isinstance(string, str):
            return locale.strcoll(string.lower(), compareString.lower())
        return eval("%s.localeCompare(%s)" % (vars_name, compareString))    
    """
    return x.replace("\n    ", "\n")


def local_length():
    x = """
    def __ee_extra_length(string):
        vars_name = varName(string)
        if isinstance(string, str):
            return len(string)
        elif isinstance(string, list):
            return len(string)
        return eval("%s.length" % vars_name)    
    """
    return x.replace("\n    ", "\n")


def local_match():
    x = """
    def __ee_extra_match(string, regexp):
        vars_name = varName(string)
        if isinstance(string, str):
            if regex.match(regexp, string) is None:
                return None
            return regex.match(regexp, string).group()
        return eval("%s.match(%s)" % (vars_name, regexp))    
    """
    return x.replace("\n    ", "\n")


def local_search():
    x = """
    def __ee_extra_search(string, regexp):
        vars_name = varName(string)
        if isinstance(string, str):
            if regex.search(regexp, string) is None:
                return None
            return regex.search(regexp, string).start()
        return eval("%s.search(%s)" % (vars_name, regexp))    
    """
    return x.replace("\n    ", "\n")


def local_slice():
    x = """
    def __ee_extra_slice(iterable, start=None, end=None):
        vars_name = varName(iterable)
        if start is None:
            start = 0
        if end is None:
            end = len(iterable)
        if isinstance(iterable, str):
            return iterable[start:end]
        elif isinstance(iterable, list):
            return iterable[start:end]
        return eval("%s.slice(%s, %s)" % (vars_name, start, end))
    """
    return x.replace("\n    ", "\n")


def local_substr():
    x = """
    def __ee_extra_substr(string, start, length):
        vars_name = varName(string)
        if isinstance(string, str):
            return string[start:][:(length -1)]
        return eval("%s.substr(%s, %s)" % (vars_name, start, length))    
    """
    return x.replace("\n    ", "\n")


def local_substring():
    x = """
    def __ee_extra_substring(string, start, end):
        vars_name = varName(string)
        if isinstance(string, str):
            return string[start:end]
        return eval("%s.substring(%s, %s)" % (vars_name, start, end))    
    """
    return x.replace("\n    ", "\n")


def local_toLowerCase():
    x = """
    def __ee_extra_toLowerCase(string):
        vars_name = varName(string)
        if isinstance(string, str):
            return string.lower()
        return eval("%s.toLowerCase()" % vars_name)    
    """
    return x.replace("\n    ", "\n")


def local_toUpperCase():
    x = """
    def __ee_extra_toUpperCase(string):
        vars_name = varName(string)
        if isinstance(string, str):
            return string.upper()
        return eval("%s.toUpperCase()" % vars_name)    
    """
    return x.replace("\n    ", "\n")


def local_toString():
    x = """
    def __ee_extra_toString(string):
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


def local_trim():
    x = """
    def __ee_extra_trim(string):
        vars_name = varName(string)
        if isinstance(string, str):
            return string.strip()
        return eval("%s.trim()" % vars_name)
    """
    return x.replace("\n    ", "\n")


def local_every():
    x = """
    def __ee_extra_every(array, function):
        vars_name = varName(array)
        if isinstance(array, list):
            return all(list(map(function, array)))
        return eval("%s.every(%s)" % (vars_name, function.__name__))
    """
    return x.replace("\n    ", "\n")


def local_filter():
    x = """
    def __ee_extra_filter(array, function):
        vars_name = varName(array)
        if isinstance(array, list):
            return list(filter(function, array))
        return eval("%s.filter(%s)" % (vars_name, function.__name__))
    """
    return x.replace("\n    ", "\n")


def local_foreach():
    x = """
    def __ee_extra_foreach(array, function):
        vars_name = varName(array)
        if isinstance(array, list):        
            for index, element in enumerate(array):
                try:
                    try:
                        function(element)
                    except:
                        function(element, index)
                except:
                    warnings.warn("Sorry ee_extra does not support complex forEach yet.")
                    return "%s.forEach(%s)" % (vars_name, function.__name__)
        return eval("%s.forEach(%s)" % (vars_name, function.__name__))
    """
    return x.replace("\n    ", "\n")


def local_arrayfrom():
    x = """
    from collections.abc import Iterable
    def __ee_extra_arrayfrom(iterable):
        vars_name = varName(iterable)
        if isinstance(iterable, Iterable):
            return list(iterable)
        return eval("Array.from(%s)" % (vars_name))
    """
    return x.replace("\n    ", "\n")


def local_isArray():
    x = """
    def __ee_extra_isArray(array):
        vars_name = varName(array)
        if isinstance(array, list):
            return True
        return False
    """
    return x.replace("\n    ", "\n")


def local_join():
    x = """
    def __ee_extra_join(array, separator=","):
        vars_name = varName(array)
        if isinstance(array, list):
            newarray = [str(element) for element in array]
            return separator.join(newarray)
        return eval("%s.join(%s)" % (vars_name, separator))
    """
    return x.replace("\n    ", "\n")


def local_map():
    x = """
    def __ee_extra_map(array, function):
        vars_name = varName(array)
        if isinstance(array, list):
            return list(map(function, array))
        return eval("%s.map(%s)" % (vars_name, function.__name__))
    """
    return x.replace("\n    ", "\n")


def local_push():
    x = """
    def __ee_extra_push(array, *args):
        vars_name = varName(array)
        if isinstance(array, list):
            exec("global %s" % vars_name)
            exec("%s.extend(%s)" % (vars_name, args))
            return len(array)
        return eval("%s.push(%s)" % (vars_name, *args))
    """
    return x.replace("\n    ", "\n")


def local_reduce():
    x = """
    def __ee_extra_reduce(array, function):
        vars_name = varName(array)
        if isinstance(array, list):
            import functools
            return functools.reduce(function, array)
        return eval("%s.reduce(%s)" % (vars_name, function.__name__))
    """
    return x.replace("\n    ", "\n")


def local_reduceRight():
    x = """
    def __ee_extra_reduceRight(array, function):
        vars_name = varName(array)
        if isinstance(array, list):
            import functools
            return functools.reduce(function, array[::-1])
        return eval("%s.reduceRight(%s)" % (vars_name, function.__name__))
    """
    return x.replace("\n    ", "\n")


def local_shift():
    x = """
    def __ee_extra_shift(array):
        vars_name = varName(array)
        if isinstance(array, list):
            exec("global %s" % vars_name)
            toreturn = array[0]
            del array[0]
            return toreturn
        return eval("%s.shift()" % (vars_name))
    """
    return x.replace("\n    ", "\n")


def local_some():
    x = """
    def __ee_extra_some(array, function):
        vars_name = varName(array)
        if isinstance(array, list):
            return any(list(map(function, array)))
        return eval("%s.some(%s)" % (vars_name, function.__name__))
    """
    return x.replace("\n    ", "\n")


def local_splice():
    x = """
    def __ee_extra_splice(array, index=None, howmany=None, *args):
        vars_name = varName(array)
        if index is None:
            index = 0
        if howmany is None:
            howmany = len(array)
                        
        if isinstance(array, list):
            exec("global %s" % vars_name)
            to_return = array[index:index+howmany]
            if len(args) == 0:
                for to_remove in range(howmany):
                    exec("del %s[%s]" % (vars_name, index))
                return to_return
            else:
                for to_remove in range(howmany):
                    exec("del %s[%s]" % (vars_name, index))
                for to_add in args[::-1]:
                    try:
                        exec("%s.insert(%s, %s)" % (vars_name, index, to_add))
                    except:
                        exec("%s.insert(%s, '%s')" % (vars_name, index, to_add))
                return to_return
        args = [str(arg)for arg in args]
        return eval("%s.splice(%s, %s, %s)" % (vars_name, index, howmany, ", ".join(args)))    
    """
    return x.replace("\n    ", "\n")


def local_unshift():
    x = """
    def __ee_extra_unshift(array, *args):
        vars_name = varName(array)
        if isinstance(array, list):
            if vars_name is not None:
                exec("global %s" % vars_name)
                for arg in args[::-1]:
                    try:
                        exec("%s.insert(0, %s)" % (vars_name, arg))
                    except:
                        exec("%s.insert(0, '%s')" % (vars_name, arg))
                return len(array)
            else:
                return len(args) + len(array)
        args = [str(arg)for arg in args]        
        return eval("%s.unshift(%s)" % (vars_name, ", ".join(args)))
    """
    return x.replace("\n    ", "\n")


def local_valueOf():
    x = """
    def __ee_extra_valueOf(array):
        vars_name = varName(array)
        if isinstance(array, list):
            return array
        return eval("%s.valueOf()" % (vars_name))
    """
    return x.replace("\n    ", "\n")
