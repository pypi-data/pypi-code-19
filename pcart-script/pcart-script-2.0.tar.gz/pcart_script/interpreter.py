from functools import reduce
from decimal import Decimal


class LispInterpreter:

    def __init__(self, code=None, s_expr=None, globals={}):
        self.code = code
        self.s_expr = s_expr
        self.debug_output = []
        self.globals = {
            '+': self.add,
            '-': self.sub,
            '*': self.mult,
            '/': self.div,

            'eq?': self.eq,
            '==': self.eq,
            'neq?': self.neq,
            '!=': self.neq,
            'gt?': self.gt,
            '>': self.gt,
            'geq?': self.geq,
            '>=': self.geq,
            'lt?': self.lt,
            '<': self.lt,
            'leq?': self.leq,
            '<=': self.leq,
            '<%': self.lt_percent,
            '<=%': self.leq_percent,
            '>%': self.gt_percent,
            '>=%': self.geq_percent,

            'not': self._not,
            'and': self._and,
            'or': self._or,

            'car': self.car,
            'cdr': self.cdr,
            'min': self.min,
            'max': self.max,
            'apply': self.apply,
            'map': self.map,
            'filter': self.filter,
            'reduce': self.reduce,

            'begin': self.begin,
            'print': self.print,
            'debug': self.debug,

            'get': self._get,

            'float': self.to_float,
            'int': self.to_int,
            'str': str,
            'else': self._else,

            'roundup': self.roundup,
            'days_till_now': self.days_till_now,

            'keys': self._keys,
            'list': self._list,

            'str': self.to_str,
            'strip': self._strip,
            'concat': self.concat,
            'join': self._join,
            'split': self._split,
        }
        self.globals.update(globals)

    @staticmethod
    def _split(value, delim=' '):
        return str(value).split(delim)

    @staticmethod
    def _join(delim, *args):
        return str(delim).join([str(x) for x in args])

    @staticmethod
    def concat(*args):
        return ''.join([str(x) for x in args])

    @staticmethod
    def to_str(value):
        return str(value)

    @staticmethod
    def _strip(value):
        return str(value).strip()

    @staticmethod
    def _list(*args):
        return list(args)

    @staticmethod
    def to_int(value):
        result = int(value.replace(',', '.').replace('/', '.').replace(' ', '').strip())
        return result

    @staticmethod
    def to_float(value):
        result = float(value.replace(',', '.').replace('/', '.').replace(' ', '').strip())
        return result

    @staticmethod
    def days_till_now(date):
        from django.utils.timezone import now
        delta = now() - date
        return delta.days

    @staticmethod
    def roundup(value, base=1):
        import math
        if isinstance(value, Decimal):
            return int(math.ceil(Decimal(value) / Decimal(base))) * Decimal(base)
        else:
            return int(math.ceil(value / base)) * base

    @staticmethod
    def _else(*args):
        return False

    @staticmethod
    def _keys(obj):
        return list(obj.keys())

    @staticmethod
    def _get(obj, attr, default=None):
        try:
            return obj[attr]
        except KeyError:
            return default
        except IndexError:
            return default

    @staticmethod
    def car(*args):
        if len(args) > 0:
            return args[0]
        else:
            return None

    @staticmethod
    def cdr(*args):
        return args[1:]

    @staticmethod
    def min(*args):
        return min(*args)

    @staticmethod
    def max(*args):
        return max(*args)

    @staticmethod
    def add(*args):
        has_decimals = list(filter(lambda x: isinstance(x, Decimal), args))
        if has_decimals:
            return reduce(lambda a, b: Decimal(a) + Decimal(b), args)
        else:
            return reduce(lambda a, b: a+b, args)

    @staticmethod
    def sub(*args):
        if len(args) == 1:
            return -args[0]

        has_decimals = list(filter(lambda x: isinstance(x, Decimal), args))
        if has_decimals:
            return reduce(lambda a, b: Decimal(a) - Decimal(b), args)
        else:
            return reduce(lambda a, b: a-b, args)

    @staticmethod
    def mult(*args):
        has_decimals = list(filter(lambda x: isinstance(x, Decimal), args))
        if has_decimals:
            return reduce(lambda a, b: Decimal(a) * Decimal(b), args)
        else:
            return reduce(lambda a, b: a*b, args)

    @staticmethod
    def div(*args):
        has_decimals = list(filter(lambda x: isinstance(x, Decimal), args))
        if has_decimals:
            return reduce(lambda a, b: Decimal(a) / Decimal(b), args)
        else:
            return reduce(lambda a, b: a/b, args)

    @staticmethod
    def eq(*args):
        return reduce(lambda a, b: a == b, args)

    @staticmethod
    def begin(*args):
        return args[-1]

    @staticmethod
    def neq(*args):
        return reduce(lambda a, b: a != b, args)

    @staticmethod
    def gt(*args):
        return reduce(lambda a, b: a > b, args)

    @staticmethod
    def geq(*args):
        return reduce(lambda a, b: a >= b, args)

    @staticmethod
    def lt(*args):
        return reduce(lambda a, b: a < b, args)

    @staticmethod
    def leq(*args):
        return reduce(lambda a, b: a <= b, args)

    @staticmethod
    def lt_percent(a, b, ratio):
        return (abs(a - b) / min([a, b])) < ratio

    @staticmethod
    def leq_percent(a, b, ratio):
        return (abs(a - b) / min([a, b])) <= ratio

    @staticmethod
    def gt_percent(a, b, ratio):
        return (abs(a - b) / min([a, b])) > ratio

    @staticmethod
    def geq_percent(a, b, ratio):
        return (abs(a - b) / min([a, b])) >= ratio

    @staticmethod
    def _not(*args):
        return not(reduce(lambda a, b: a and b, args))

    @staticmethod
    def _or(*args):
        return reduce(lambda a, b: a or b, args)

    @staticmethod
    def _and(*args):
        return reduce(lambda a, b: a and b, args)

    @staticmethod
    def apply(fn, args):
        return fn(*args)

    @staticmethod
    def map(fn, *args):
        return list([fn(x) for x in args])

    @staticmethod
    def filter(fn, *args):
        return list([x for x in args if fn(x)])

    @staticmethod
    def reduce(fn, *args):
        return reduce(fn, args)

    @staticmethod
    def print(*args):
        return print(*args)

    def debug(self, *args):
        self.debug_output.append(list([str(x) for x in args]))
        if len(args) > 0:
            return args[-1]

    def parse_s_expression(self):
        from sexpdata import loads
        return loads(self.code, true='#t', false='#f')

    def eval(self, list_or_atom):
        from sexpdata import Symbol
        if isinstance(list_or_atom, list):
            if len(list_or_atom) > 0:
                if list_or_atom[0] == Symbol('lambda'):
                    result = self.create_procedure(
                        list([x.value() for x in list_or_atom[1]]),
                        list(list_or_atom[2]),
                        self.globals,
                    )
                    return result
                elif list_or_atom[0] == Symbol('if'):
                    expression = self.eval_symbol(list_or_atom[1])
                    result = None
                    if len(list_or_atom) == 4:
                        result = self.eval_symbol(list_or_atom[2]) if expression else self.eval_symbol(list_or_atom[3])
                    elif len(list_or_atom) == 3:
                        result = self.eval_symbol(list_or_atom[2]) if expression else None
                    return result
                elif list_or_atom[0] == Symbol('unless'):
                    expression = self.eval_symbol(list_or_atom[1])
                    result = None
                    if len(list_or_atom) == 4:
                        result = self.eval_symbol(list_or_atom[2]) if not expression else self.eval_symbol(list_or_atom[3])
                    elif len(list_or_atom) == 3:
                        result = self.eval_symbol(list_or_atom[2]) if not expression else None
                    return result
                elif list_or_atom[0] == Symbol('cond'):
                    result = None
                    for expr in list_or_atom[1:]:
                        *conds, value = expr
                        chunks = list([self.eval_symbol(item) for item in conds])
                        condition = any(chunks)
                        if condition:
                            result = self.eval_symbol(value)
                            break
                    return result
                elif list_or_atom[0] == Symbol('struct'):
                    result = dict()
                    for expr in list_or_atom[1:]:
                        index, value = expr
                        index = self.eval_symbol(index)
                        if index:
                            result[index] = self.eval_symbol(value)
                    return result
                elif list_or_atom[0] in [Symbol('define'), Symbol('set!')]:
                    symbol = list_or_atom[1].value()
                    self.globals[symbol] = self.eval_symbol(list_or_atom[2])
                    return self.globals[symbol]
                else:
                    fn, *fn_args = [self.eval_symbol(item) for item in list_or_atom]
                    try:
                        result = fn(*fn_args)
                        return result
                    except Exception as e:
                        raise Exception('%s - func:%s args:%s' % (e, fn.__name__, fn_args))
        return self.eval_symbol(list_or_atom)

    def eval_symbol(self, symbol):
        from sexpdata import Symbol, Quoted
        if isinstance(symbol, Symbol):
            _s = symbol.value()
            if '.' in _s:
                chunks = _s.split('.')
                value = self.globals
                for i in chunks:
                    if hasattr(value, 'get'):
                        value = value.get(i)
                    else:
                        raise Exception('Cannot find "%s" in "%s"' % (i, _s))
                return value
            else:
                return self.globals.get(_s)
        elif isinstance(symbol, Quoted):
            return symbol.value()
        elif isinstance(symbol, list):
            return self.eval(symbol)
        else:
            return symbol

    def execute(self):
        if self.s_expr is None and self.code is not None:
            if not self.code:
                return None
            s_expr = self.parse_s_expression()
            result = self.eval(s_expr)
        else:
            result = self.eval(self.s_expr)
        return result

    @staticmethod
    def create_procedure(params, s_expr, globals={}):
        def procedure_body(*args):
            kwargs = dict(zip(params, args))
            locals = globals
            locals.update(kwargs)
            interpreter = LispInterpreter(s_expr=s_expr, globals=locals)
            return interpreter.execute()
        return procedure_body
