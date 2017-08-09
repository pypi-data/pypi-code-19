"""Tools for working with function and code objects"""

from types import FunctionType, CodeType, MethodType
import copy as _copy
import functools


__all__ = (
    'CODE_ATTR', 'CLOSURE_ATTR', 'NAME_ATTR',
    'GLOBALS_ATTR', 'DEFAULTS_ATTR', 'DICT_ATTR',

    'METHOD_FUNC_ATTR', 'METHOD_SELF_ATTR', 'METHOD_HAS_CLASS',

    'CODE_ARGS', 'FUNCTION_ARGS', 'METHOD_ARGS',

    'copy', 'deepcopy', 'is_copy', 'set_attr', 'get_attr'
)

if hasattr(FunctionType, '__code__'):
    CODE_ATTR = '__code__'
    GLOBALS_ATTR = '__globals__'
    NAME_ATTR = '__name__'
    DEFAULTS_ATTR = '__defaults__'
    CLOSURE_ATTR = '__closure__'
else:
    CODE_ATTR = 'func_code'
    GLOBALS_ATTR = 'func_globals'
    NAME_ATTR = 'func_name'
    DEFAULTS_ATTR = 'func_defaults'
    CLOSURE_ATTR = 'func_closure'

if hasattr(FunctionType, '__dict__'):
    DICT_ATTR = '__dict__'
else:
    DICT_ATTR = 'func_dict'

FUNCTION_ARGS = (
    CODE_ATTR, GLOBALS_ATTR, NAME_ATTR, DEFAULTS_ATTR, CLOSURE_ATTR
)

if hasattr(MethodType, '__self__'):
    METHOD_FUNC_ATTR = '__func__'
    METHOD_SELF_ATTR = '__self__'
else:
    METHOD_FUNC_ATTR = 'im_func'
    METHOD_SELF_ATTR = 'im_self'

METHOD_HAS_CLASS = hasattr(MethodType, 'im_class')
if METHOD_HAS_CLASS:
    METHOD_ARGS = METHOD_FUNC_ATTR, METHOD_SELF_ATTR, 'im_class'
else:
    METHOD_ARGS = METHOD_FUNC_ATTR, METHOD_SELF_ATTR

HAS_KWARGS = hasattr(CodeType, 'co_kwonlyargcount')

if HAS_KWARGS:
    CODE_ARGS = (
        'co_argcount', 'co_kwonlyargcount', 'co_nlocals', 'co_stacksize',
        'co_flags', 'co_code', 'co_consts', 'co_names', 'co_varnames',
        'co_filename', 'co_name', 'co_firstlineno', 'co_lnotab', 'co_freevars',
        'co_cellvars'
    )
else:
    CODE_ARGS = (
        'co_argcount',                      'co_nlocals', 'co_stacksize',
        'co_flags', 'co_code', 'co_consts', 'co_names', 'co_varnames',
        'co_filename', 'co_name', 'co_firstlineno', 'co_lnotab', 'co_freevars',
        'co_cellvars'
    )


def copy(x):
    if isinstance(x, FunctionType):
        args = [copy(getattr(x, CODE_ATTR))]
        args.extend(getattr(x, i) for i in FUNCTION_ARGS[1:])
        f = FunctionType(*args)
        getattr(f, DICT_ATTR).update(getattr(x, DICT_ATTR, {}))
        return functools.wraps(x)(f)
    if isinstance(x, CodeType):
        return CodeType(*[getattr(x, i) for i in CODE_ARGS])
    try:
        return _copy.copy(x)
    except:
        return x


def deepcopy(x):
    if isinstance(x, FunctionType):
        f = FunctionType(*[deepcopy(getattr(x, i)) for i in FUNCTION_ARGS])
        func_dict = getattr(x, DICT_ATTR, {})
        getattr(f, DICT_ATTR).update({deepcopy(k): deepcopy(func_dict[k]) for k in func_dict})
        return functools.wraps(x)(f)
    if isinstance(x, CodeType):
        return CodeType(*[deepcopy(getattr(x, i)) for i in CODE_ARGS])
    try:
        return _copy.deepcopy(x)
    except:
        try:
            return copy(x)
        except:
            return x


_ATTRIBUTE_ALIASES = {
    'const': 'consts',
    'constants': 'consts'
}.get


def _normalise_func_attr(attribute):
    has_func_prefix = attribute.startswith('func_')
    has_co_prefix = attribute.startswith('co_')
    is_dunder = attribute.startswith('__') and attribute.endswith('__') and len(attribute) > 3
    needs_dunder = CODE_ATTR.startswith('__')
    if has_func_prefix:
        bare = attribute[5:]
        bare = _ATTRIBUTE_ALIASES(bare, bare)
        attribute = 'func_' + bare
    elif is_dunder:
        bare = attribute[2:-2]
        bare = _ATTRIBUTE_ALIASES(bare, bare)
        attribute = '__' + bare + '__'
    elif has_co_prefix:
        bare = attribute[3:]
        bare = _ATTRIBUTE_ALIASES(bare, bare)
        attribute = 'co_' + bare
    else:
        attribute = bare = _ATTRIBUTE_ALIASES(attribute, attribute)
    if has_func_prefix or is_dunder:
        if needs_dunder:
            if has_func_prefix:
                attribute = '__' + bare + '__'
        elif is_dunder:
            attribute = 'func_' + bare
        if attribute in FUNCTION_ARGS:
            return False, attribute
    elif has_co_prefix:
        if attribute in CODE_ARGS:
            return True, attribute
    else:
        if needs_dunder:
            possible_function_arg = '__' + attribute + '__'
        else:
            possible_function_arg = 'func_' + attribute
        if possible_function_arg in FUNCTION_ARGS:
            return False, possible_function_arg
        possible_code_arg = 'co_' + attribute
        if possible_code_arg in CODE_ARGS:
            return True, possible_code_arg
    raise ValueError('Unknown attribute {!r}'.format(attribute))


def set_attr(f, *args, **kwargs):
    if len(args) == 2:
        if kwargs:
            raise TypeError('Expected no keyword arguments if there are 2 positional arguments')
        return _set_attr(f, *args)
    if not args:
        return _set_attrs(f, **kwargs)
    raise TypeError('Expected either 2 or 0 positional arguments, got {}'.format(len(args)))


def _set_attr(f, attribute, new_value):
    f = deepcopy(f)
    is_code_arg, attribute = _normalise_func_attr(attribute)

    if is_code_arg:
        code = getattr(f, CODE_ATTR)
        code = CodeType(*(
            new_value if i == attribute else getattr(code, i)
            for i in CODE_ARGS
        ))
        setattr(f, CODE_ATTR, code)
    else:
        setattr(f, attribute, new_value)
    return f


def _set_attrs(f, **new_attributes):
    normalised = {}
    for attr in new_attributes:
        value = new_attributes[attr]
        is_code_arg, norm_attr = _normalise_func_attr(attr)
        if norm_attr in normalised:
            if norm_attr == CODE_ATTR and isinstance(value, CodeType) and type(normalised[CODE_ATTR]) is type(b''):
                normalised['co_code'] = normalised[CODE_ATTR]
            else:
                raise ValueError('Duplicate entry for {}'.format(norm_attr))
        normalised[norm_attr] = is_code_arg, value

    f = deepcopy(f)
    if CODE_ATTR in normalised:
        for attr in normalised:
            is_code_arg, value = normalised[attr]
            if is_code_arg:
                raise ValueError(
                    'Cannot set {0!r} and attributes of {0!r} at the same time'.format(CODE_ATTR)
                )
            setattr(f, attr, value)
        return f
    code = getattr(f, CODE_ATTR)
    code_args = [getattr(code, i) for i in CODE_ARGS]
    for attr in normalised:
        is_code_arg, value = normalised[attr]
        if is_code_arg:
            code_args[CODE_ARGS.index(attr)] = value
        else:
            setattr(f, attr, value)
    setattr(f, CODE_ATTR, CodeType(*code_args))
    return f


def get_attr(f, attribute):
    is_code_arg, attribute = _normalise_func_attr(attribute)
    if is_code_arg:
        return getattr(getattr(f, CODE_ATTR), attribute)
    return getattr(f, attribute)


def _empty():
    pass

DEFAULT_FLAGS = get_attr(_empty, 'co_flags')
