import ast
import re
import sys

from numpydoc.docscrape import NumpyDocString, FunctionDoc, ClassDoc
import types
import inspect
import larray as la


def get_defaults(func):
    spec = inspect.getfullargspec(func)
    if spec.defaults is None:
        return {}
    else:
        defaults = spec.defaults
        return dict(zip(spec.args[-len(defaults):], defaults))

NO_DEFAULT_VALUE = object()


def get_params(obj):
    if not hasattr(obj, '__name__') or not hasattr(obj, '__doc__'):
        return
    docstring = obj.__doc__
    if docstring is None:
        return

    if isinstance(obj, types.FunctionType):
        doc = FunctionDoc(obj)
    elif isinstance(obj, type):
        doc = ClassDoc(obj)
    else:
        doc = NumpyDocString(docstring)
    try:
        defaults = get_defaults(obj)
    except Exception:
        return

    params = []
    # print(list(doc.keys()))
    # print(doc['Signature'])
    for name, type_, desc in doc['Parameters']:
        optional = ', optional' in type_
        if optional:
            type_ = type_.replace(', optional', '')

        if optional and name not in defaults:
            print("WARNING: optional but no default value")
        elif not optional and name in defaults:
            print("WARNING: default value but no optional")

        if '{' in type_ and '}' in type_:
            try:
                options = ast.literal_eval(type_)
                type_ = sorted(options)
            except (SyntaxError, ValueError) as e:
                print("exception", e)

        # TODO: remove "Defaults to" from desc
        params.append((name, type_, defaults.get(name, NO_DEFAULT_VALUE), '\n'.join(desc)))
    return params


def show_params(obj):
    params = get_params(obj)
    if params is None:
        return

    objname = obj.__name__

    print()
    print(objname)
    print("=" * len(objname))
    for name, type_, default, desc in params:
        if default is NO_DEFAULT_VALUE:
            default = '<no default value>'
        else:
            default = repr(default)
        print(name, ":", type_, "=", default)
        print(" " * 3, desc)


def show_all(container):
    for objname in dir(container):
        if objname.startswith('_'):
            continue

        obj = getattr(container, objname)
        if isinstance(obj, str):
            continue

        if isinstance(obj, types.ModuleType):
            continue

        show_params(obj)

show_params(la.LArray.append)
show_params(la.LArray.diff)
show_params(la.LArray.percentile)
# show_all(la)

# print()
# print("##########")
# print("# LArray #")
# print("##########")
# show_all(la.LArray)
