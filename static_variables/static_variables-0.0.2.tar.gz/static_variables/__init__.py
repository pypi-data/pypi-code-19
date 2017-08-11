"""Static variables (dynamic constant references) for Python."""

import dis
import itertools
import types
try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

import static_variables.opcode_desc as opcode_desc
import static_variables.codetools as codetools

__all__ = ('static', 'resolve_static', 'EMPTY_SET')


__author__ = 'Mital Ashok'
__credits__ = ['Mital Ashok']
__license__ = 'MIT'
__version__ = '0.0.2'
__maintainer__ = 'Mital Ashok'
__author_email__ = __email__ = 'mital.vaja@googlemail.com'
__status__ = 'Development'

EMPTY_SET = set()

# _flag_name_map = {name: mask for mask, name in dis.COMPILER_FLAG_NAMES.items()}
# _FLAG_MASK = ~(
#     _flag_name_map['VARARGS'] |
#     _flag_name_map['VARKEYWORDS'] |
#     _flag_name_map['GENERATOR'] |
#     _flag_name_map['ITERABLE_COROUTINE'] |
#     _flag_name_map['ASYNC_GENERATOR']
# )

_FLAG_MASK = ~0b1100101100

_GET_ATTRIBUTE = {
    'co_flags': codetools.attr_getter('co_flags'),
    'co_consts': codetools.attr_getter('co_consts')
}


def static(expression):
    # TYPE_CHECKING is always False but a
    # static analyser should take it to be True
    if TYPE_CHECKING:
        return expression
    raise RuntimeError(
        '`static` has been called at runtime. '
        'Perhaps you forgot to add the @resolve_static decorator?'
    )


def _evaluate_static(f, code):
    kwargs = {
        'co_argcount': 0,
        'co_flags': _GET_ATTRIBUTE['co_flags'](f) & _FLAG_MASK,
        'co_code': code
    }
    if codetools.HAS_KWARGS:
        kwargs['co_kwonlyargcount'] = 0
    f = codetools.set_attr(f, **kwargs)
    return f()


def resolve_static(f=None, empty_set_literal=False):
    if f is None:
        def decorator(f):
            return resolve_static(f, empty_set_literal=empty_set_literal)
        return decorator
    if TYPE_CHECKING:
        return f
    if isinstance(f, types.MethodType):
        args = [getattr(f, arg) for arg in codetools.METHOD_ARGS]
        args[0] = resolve_static(args[0])
        return types.MethodType(*args)
    new_code = []
    stack_length = 0
    static_code = []
    constants = list(_GET_ATTRIBUTE['co_consts'](f))
    const_index = itertools.count(len(constants))
    in_static = False
    for i in dis.Bytecode(f):
        if (
            (i.argval == 'EMPTY_SET' and i.opname == 'LOAD_GLOBAL') or
            (empty_set_literal and i.argval == 0 and i.opname == 'BUILD_MAP')
        ):
            c = opcode_desc.create_instruction('BUILD_SET', 0)
            i = next(c)
            if next(c, False):
                raise RuntimeError('BUILD_SET opcode with arg of 0 is extended?')
        if i.argval == 'static' and opcode_desc.is_non_global_scope_getter(i.opname):
            raise SyntaxError('No variables named `static` are allowed')
        if i.opname == 'LOAD_GLOBAL' and i.argval == 'static':
            if stack_length != 0 or static_code or in_static:
                raise SyntaxError('Do not nest `static()`')
            in_static = True
        elif in_static:
            stack_length += opcode_desc.get_stack_change(i)
            if stack_length > 0:
                static_code.append(i)
            elif stack_length < 0:
                raise RuntimeError('Somehow got negative stack length!')
            else:
                if i.opname != 'CALL_FUNCTION' or i.argval != 1:
                    raise SyntaxError('Must call `static` with one positional argument')
                static_code.extend(opcode_desc.create_instruction('RETURN_VALUE', None, None, '', i.offset, i.starts_line, False))
                next_constant = _evaluate_static(f, opcode_desc.reassemble(static_code))
                constants.append(next_constant)
                static_code = []
                new_code.extend(opcode_desc.create_instruction('LOAD_CONST', next(const_index), next_constant, '<avoid calling repr() on arbitrary objects>', i.offset, i.starts_line, False))
                in_static = False
        else:
            new_code.append(i)
    new_f = codetools.set_attr(f, co_consts=tuple(constants), co_code=opcode_desc.reassemble(new_code))
    new_f.__wrapped__ = f
    return new_f


def check_static():
    """
    Checks whether `resolve_static` works. May segfault.

    If it works, return 0.

    Otherwise, set `static` and `resolve_static` to dummy functions with `__defunct` set to `True`.
    """
    global static, resolve_static
    if hasattr(static, '__defunct'):
        return 1
    try:
        @resolve_static
        def f():
            return static([])

        ls = f()
        if f() is not ls:
            del f, ls
            raise RuntimeError()
        f().append(1)
        if f() != [1]:
            del f, ls
            raise RuntimeError()
        del f, ls

        static.__defunct = False
        resolve_static.__defunct = False
        return 0
    except BaseException:
        pass
    import warnings

    def static(expression):
        warnings.warn(RuntimeWarning('`static` doesn\'t seem to work on this platform'))
        return expression

    def resolve_static(f=None, empty_set_literal=False):
        warnings.warn(RuntimeWarning('`static` doesn\'t seem to work on this platform'))
        if f is None:
            def decorator(f):
                return f
            return decorator
        return f

    static.__defunct = True
    resolve_static.__defunct = True
    return 1

if __name__ == '__main__':
    status = check_static()
    if status != 0:
        import sys

        sys.exit(status)

    del status
