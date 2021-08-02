"""
ee_extra Extensions.
"""

__version__ = "0.0.2"

# warnings.simplefilter("always", UserWarning)


class Container(dict):
    """Container of classes and methods."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]


def merge(dict1, dict2):
    """Nested merge of dictionaries"""
    output = Container()

    # adds keys from `dict1` if they do not exist in `dict2` and vice-versa
    intersection = Container({**dict2, **dict1})

    for k_intersect, v_intersect in intersection.items():
        if k_intersect not in dict1:
            v_dict2 = dict2[k_intersect]
            output[k_intersect] = v_dict2

        elif k_intersect not in dict2:
            output[k_intersect] = v_intersect

        elif isinstance(v_intersect, dict):
            v_dict2 = dict2[k_intersect]
            output[k_intersect] = merge(v_intersect, v_dict2)

        else:
            output[k_intersect] = v_intersect

    return output


class ExtraFunctions:
    def __init__(self):
        self.functions = {}

    def add(self, subpackage, module, funame):
        def wrapper(function):
            container_sub = Container()
            container_mod = Container()
            container_fun = Container()
            container_fun[funame] = function
            if subpackage is None:
                if module is None:
                    self.functions = merge(self.functions, container_fun)
                else:
                    container_mod[module] = container_fun
                    self.functions = merge(self.functions, container_mod)
            else:
                container_mod[module] = container_fun
                container_sub[subpackage] = container_mod
                self.functions = merge(self.functions, container_sub)

        return wrapper


# Dictionary to save functions
Extra = ExtraFunctions()

from ee_extra.Image.basic import *
from ee_extra.ImageCollection.core import *
from ee_extra.Spectral import core
from ee_extra.STAC import core

Extra = Extra.functions
