import keyword
import types

__author__ = 'Michael'


def split_var_func(d):
    var_dict = dict()
    func_dict = dict()
    for key in d:
        val = d[key]
        if isinstance(val, types.FunctionType) \
                or isinstance(val, types.BuiltinFunctionType) \
                or isinstance(val, types.BuiltinMethodType):
            func_dict[key] = val
        else:
            var_dict[key] = val
    return var_dict, func_dict


PyCalc_Keywords = ["exit", "reset", "clear", "show"]


def valid_var_name(name):
    if keyword.iskeyword(name):
        return False
    if name in PyCalc_Keywords:
        return False
    if not (name[0].isalpha() or name[0] == "_"):
        return False
    for i in name[1:]:
        if not (i.isalnum() or i == "_"):
            return False
    return True


from . import terminal
