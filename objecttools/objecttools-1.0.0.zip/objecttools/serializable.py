"""Create serializable versions of objects that can be pickled"""

import collections
import types

from objecttools import ThreadedCachedProperty, Singleton

__all__ = ('SerializableFunction', 'SerializableCode', 'SerializableConstant')

_Missing = Singleton.create('_Missing', object_name='_missing')
_missing = _Missing()

if hasattr(types.FunctionType, '__code__'):
    CODE_ATTR = '__code__'
    GLOBALS_ATTR = '__globals__'
    NAME_ATTR = '__name__'
    DEFAULTS_ATTR = '__defaults__'
    CLOSURE_ATTR = '__closure__'
    DICT_ATTR = '__dict__'
else:
    CODE_ATTR = 'func_code'
    GLOBALS_ATTR = 'func_globals'
    NAME_ATTR = 'func_name'
    DEFAULTS_ATTR = 'func_defaults'
    CLOSURE_ATTR = 'func_closure'
    DICT_ATTR = 'func_dict'

if hasattr(types.MethodType, '__func__'):
    METHOD_FUNC_ATTR = '__func__'
    METHOD_SELF_ATTR = '__self__'
else:
    METHOD_FUNC_ATTR = 'im_func'
    METHOD_SELF_ATTR = 'im_self'

METHOD_HAS_CLASS = hasattr(types.MethodType, 'im_class')

FUNCTION_ARGS = (
    CODE_ATTR, GLOBALS_ATTR, NAME_ATTR, DEFAULTS_ATTR, CLOSURE_ATTR
)

ALL_CODE_ARGS = (
    'co_argcount', 'co_kwonlyargcount', 'co_nlocals', 'co_stacksize',
    'co_flags', 'co_code', 'co_consts', 'co_names', 'co_varnames',
    'co_filename', 'co_name', 'co_firstlineno', 'co_lnotab', 'co_freevars',
    'co_cellvars'
)

if hasattr(types.CodeType, 'co_kwonlyargcount'):
    CODE_ARGS = ALL_CODE_ARGS
else:
    CODE_ARGS = (
        'co_argcount',                      'co_nlocals', 'co_stacksize',
        'co_flags', 'co_code', 'co_consts', 'co_names', 'co_varnames',
        'co_filename', 'co_name', 'co_firstlineno', 'co_lnotab', 'co_freevars',
        'co_cellvars'
    )

PY3_ATTRS = ('__kwdefaults__', '__qualname__', '__annotations__')
OPT_ATTRS = ('__wrapped__',)


class SerializableFunction(collections.namedtuple('SerializableFunction', (
    'code', 'module', 'name', 'defaults', 'closure', 'dict'
))):
    """
    Extracts attributes of a function to make it serializable.

    NOTE: All attributes set on a function must also be serializable for instances
      of this class to be serializable
    """

    def __new__(cls, f, module=None, *args):
        """
        Creates a new `SerializableFunction` instance.

        :param f: The function to decompose into a serializable form
        :type f: types.FunctionType
        :param module: Name of the module of the function (To be imported for global variables when calling).
          Leave blank to get from function (Not recommended, as it might be wrong (e.g., `"__main__"`))
        :type module: Optional[str]
        :param args: This should be ignored.
          It is used to allow `SerializableFunction(*serialized_function)` (i.e., when unpickling)
        :return: A new object that can be serialized and called
        :rtype: SerializableFunction
        """
        if args:
            if len(args) == 4:
                # When unpickling, all of the attributes are given as arguments
                return super(SerializableFunction, cls).__new__(cls, f, module, *args)
            raise TypeError('__new__() takes 1 positional argument but {} were given'.format(
                len(args) + 1
            ))
        if isinstance(f, types.MethodType):
            self = cls.__new__(cls, getattr(f, METHOD_FUNC_ATTR), module)
            self.dict['__self__'] = getattr(f, METHOD_SELF_ATTR)
            if METHOD_HAS_CLASS:
                self.dict['_SerializableFunction____self_____class__'] = f.im_class
            return self
        code = SerializableCode(getattr(f, CODE_ATTR))
        if module is None:
            module = f.__module__
        name = getattr(f, NAME_ATTR)
        defaults = getattr(f, DEFAULTS_ATTR)
        closure = getattr(f, CLOSURE_ATTR)

        d = dict(getattr(f, DICT_ATTR))
        for attr in PY3_ATTRS:
            d[attr] = getattr(f, attr, None)

        for attr in OPT_ATTRS:
            val = getattr(f, attr, _missing)
            if val is not _missing:
                d[attr] = val

        return super(SerializableFunction, cls).__new__(
            cls, code, module, name, defaults, closure, d
        )

    @ThreadedCachedProperty
    def value(self):
        """The value of `self` as an (not serializable) `types.FunctionType` object"""
        f = types.FunctionType(
            self.code.value, self.globals, self.name, self.defaults, self.closure
        )
        d = self.dict.copy()
        for attr in PY3_ATTRS:
            setattr(f, attr, d.pop(attr, None))
        for attr in OPT_ATTRS:
            val = d.pop(attr, _missing)
            if val is not _missing:
                setattr(f, attr, val)
        __self__ = d.pop('__self__', _missing)
        __class__ = d.pop('_SerializableFunction____self_____class__', _missing)
        getattr(f, DICT_ATTR).update(d)
        if __self__ is not _missing:
            if METHOD_HAS_CLASS:
                if __class__ is _missing:
                    __class__ = __self__.__class__
                f = types.MethodType(f, __self__, __class__)
            else:
                f = types.MethodType(f, __self__)
        return f

    @property
    def globals(self):
        """Find the globals of `self` by importing `self.module`"""
        return vars(__import__(self.module, fromlist=self.module.split('.')))

    def __repr__(self):
        """repr(self)"""
        name = self.dict.get('__qualname__', None)
        if name is None:
            name = self.name
        return '{}(<function {}>)'.format(type(self).__name__, name)

    def __call__(self, *args, **kwargs):
        """self(*args, **kwargs)"""
        return self.value(*args, **kwargs)

    def __getstate__(self):
        return {}

    def __setstate__(self, state):
        return


class SerializableCode(collections.namedtuple('SerializableCode', ALL_CODE_ARGS)):
    """Serializable form of `types.CodeType` objects"""

    def __new__(cls, code, *args):
        """
        Creates a new `SerializableCode` instance.

        :param code: The code object to decompose
        :type code: types.CodeType
        :param args: This should be ignored.
          It is used to allow `SerializableCode(*serialized_code)` (i.e., when unpickling)
        :return: A new object that can be serialized
        :rtype: SerializableCode
        """
        if args:
            if len(args) == 14:
                # When unpickling, all of the attributes are given as arguments
                return super(SerializableCode, cls).__new__(cls, code, *args)
            raise TypeError('__new__() takes 1 positional argument but {} were given'.format(
                len(args) + 1
            ))
        argcount = getattr(code, ALL_CODE_ARGS[0])
        kwonlyargcount = getattr(code, ALL_CODE_ARGS[1], 0)  # Not in Python 2.
        args = [argcount, kwonlyargcount]
        args.extend(getattr(code, attr) for attr in ALL_CODE_ARGS[2:])
        return super(SerializableCode, cls).__new__(cls, *args)

    @ThreadedCachedProperty
    def value(self):
        """The value of `self` as a (not serializable) `types.CodeType` object"""
        return types.CodeType(*(getattr(self, attr) for attr in CODE_ARGS))

    def __getstate__(self):
        return {}


class SerializableConstant(collections.namedtuple('SerializableConstant', ('name', 'module'))):
    """
    Serialize a constant value into the path to import it from.

    For example::

        import pickle

        from objecttools import SerializableConstant

        MODULE_CONSTANT = <some_value>

        # Even works for unpicklable objects, as long as they are module constants
        # As they are imported at unpickling time
        value = pickle.dumps(SerializableConstant('MODULE_CONSTANT', __name__))

        print(pickle.loads(value) is MODULE_CONSTANT)  # True

    """

    def __new__(cls, name, module):
        """
        Create a new `SerializableConstant` object (Or return a constant)

        :param name: The name of the constant. Will `getattr()` the module for this.
          Set to `None` for the module itself.
        :type name: Optional[str]
        :param module: The name of the module. Will import when getting the value.
        :type module: str
        :return: Union[SerializableConstant, Any]
        """
        if type(name) is not str and name is not None:
            raise TypeError('"name" must be a str')
        if type(module) is not str:
            raise TypeError('"module" must be a str')
        return super(SerializableConstant, cls).__new__(cls, name, module)

    @property
    def value(self):
        """Import the constant from `self.module`"""
        module = __import__(self.module, fromlist=self.module.split('.'))
        if self.name is None:
            return module
        return getattr(module, self.name)

    def __getstate__(self):
        return {}
