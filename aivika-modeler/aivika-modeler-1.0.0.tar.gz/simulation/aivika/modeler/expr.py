# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

class InvalidExprException(Exception):
    """Raised when the expression is invalid."""

    def __init__(self, message):
        """Initializes a new instance."""
        self.message = message

class Expr:
    """The expression that may depend on the current modeling time or transact attributes."""

    def __init__(self, model, comp):
        """Initializes a new instance."""
        self._model = model
        self._comp = comp

    def get_model(self):
        """Return the corresponding simulation model."""
        return self._model

    def read(self, transact_comp):
        """Return the corresponding computation."""
        return '(' + self._comp + ' ' + transact_comp + ')'

    def __add__(self, other):
        """Add two expressions."""
        return binary_expr(self, '+', other)

    def __sub__(self, other):
        """Subtract two expressions."""
        return binary_expr(self, '-', other)

    def __mul__(self, other):
        """Multiply two expressions."""
        return binary_expr(self, '*', other)

    def __truediv__(self, other):
        """Divide two expressions."""
        return binary_expr(self, '/', other)

    def __mod__(self, other):
        """Remainder of two expressions."""
        return binary_expr(self, '%', other)

    def __pow__(self, other):
        """The power of two expressions."""
        return binary_expr(self, '**', other)

    def __and__(self, other):
        """The AND operator."""
        return binary_expr(self, 'and', other)

    def __or__(self, other):
        """The OR operator."""
        return binary_expr(self, 'or', other)

    def __invert__(self, other):
        """The NOT operator."""
        return unnary_expr(self, 'not', other)

    def __lt__(self, other):
        """Less than."""
        return binary_expr(self, '<', other)

    def __le__(self, other):
        """Less than or equal to."""
        return binary_expr(self, '<=', other)

    def __eq__(self, other):
        """Equal to."""
        return binary_expr(self, '==', other)

    def __ne__(self, other):
        """Not equal to."""
        return binary_expr(self, '!=', other)

    def __gt__(self, other):
        """Greater than."""
        return binary_expr(self, '>', other)

    def __ge__(self, other):
        """Greater than or equal to."""
        return binary_expr(self, '>=', other)

def expect_expr(expr):
    """Expect the argument to be an expression."""
    if isinstance(expr, Expr):
        pass
    else:
        raise InvalidExprException('Expected an expression: ' + str(expr))

def expect_or_coerce_expr(model, expr):
    """Expect the argument to be an expression or coerce it to the expression."""
    if isinstance(expr, Expr):
        return expr
    elif isinstance(expr, int):
        return return_expr(model, expr)
    elif isinstance(expr, float):
        return return_expr(model, expr)
    else:
        raise InvalidExprException('Expected an expression: ' + str(expr))

def return_expr(model, value):
    """Get an expression that returns the specified constant value."""
    code = 'const (return $ ' + str(value) + ')'
    return Expr(model, code)

def time_expr(model):
    """Get an expression that returns the current modeling time."""
    code = 'const (liftDynamics time)'
    return Expr(model, code)

def start_time_expr(model):
    """Get an expression that returns the start time."""
    code = 'const (liftParameter starttime)'
    return Expr(model, code)

def stop_time_expr(model):
    """Get an expression that returns the stop time."""
    code = 'const (liftParameter stoptime)'
    return Expr(model, code)

def starttime_expr(model):
    """Get an expression that returns the start time."""
    code = 'const (liftParameter starttime)'
    return Expr(model, code)

def dt_expr(model):
    """Get an expression that returns the integration time step."""
    code = 'const (liftParameter dt)'
    return Expr(model, code)

def binary_expr(expr_1, op, expr_2):
    """Apply the specified binary operator to the expressions."""
    e1 = expr_1
    e2 = expr_2
    expect_expr(e1)
    model = e1.get_model()
    model.add_module_import('import Control.Monad')
    e2 = expect_or_coerce_expr(model, e2)
    if e1.get_model().get_main_model() != e2.get_model().get_main_model():
        raise InvalidExprException('Expected all expressions to belong to the same model')
    if op == '!=':
        op = '/='
    elif op == '%':
        op = 'mod'
    elif op == 'and':
        op = '&&'
    elif op == 'or':
        op = '||'
    elif op in ['==', '<', '>', '<=', '>=', '+', '-', '*', '/', '**']:
        pass
    else:
        raise InvalidExprException('Unrecognized binary operator: ' + op + ' (must be one of: ==, !=, <, >, <=, >=, +, -, *, /, **, %, and, or)')
    code = '(\\a -> liftM2 (' + op + ') ' + e1.read('a') + ' ' + e2.read('a') + ')'
    return Expr(model, code)

def unary_expr(op, expr):
    """Apply the specified unary operator to the expression."""
    e = expr
    expect_expr(e)
    if op == '-':
        op = 'negate'
    elif op == '+':
        op = 'id'
    elif op in ['abs', 'not', 'round']:
        pass
    else:
        raise InvalidExprException('Unrecognized unary operator: ' + op + ' (must be one of: +, -, abs, not, round)')
    model = e.get_model()
    model.add_module_import('import Data.Functor')
    code = '(\\a -> fmap (' + op + ') ' + e.read('a') + ')'
    return Expr(model, code)

def if_expr(cond_expr, true_expr, false_expr):
    """The conditional expression."""
    c = cond_expr
    t = true_expr
    f = false_expr
    expect_expr(c)
    expect_expr(t)
    expect_expr(f)
    if (c.get_model().get_main_model() != t.get_model().get_main_model()) or (c.get_model().get_main_model() != f.get_model().get_main_model()):
        raise InvalidExprException('Expected all expressions to belong to the same model')
    model = c.get_model()
    code = '(\\a -> do { f <- ' + c.read('a') + '; '
    code += 'if f then ' + t.read('a') + ' else ' + f.read('a')
    code += ' })'
    return Expr(model, code)

def int2double_expr(expr):
    """Return an expression that converts the integer value to a floating-point number."""
    e = expr
    expect_expr(e)
    model = e.get_model()
    model.add_module_import('import Data.Functor')
    code = '(\\a -> fmap (fromRational . toRational) ' + expr.read('a') + ')'
    return Expr(model, code)

def expr_sequence(exprs):
    """The sequence of expressions for performing some side-effect."""
    es = exprs
    if len(es) == 0:
        raise InvalidExprException('Expected at least one expession')
    e0 = exprs[0]
    expect_expr(e0)
    for e in es:
        expect_expr(e)
        if (e0.get_model().get_main_model() != e.get_model().get_main_model()):
            raise InvalidExprException('Expected the expressions to belong to the same model')
    model = e0.get_model()
    model.add_module_import('import Control.Monad')
    code = '(\\a -> sequence_ ['
    code += ', '.join([e.read('a') for e in es])
    code += '])'
    return Expr(model, code)
