import warnings
from sympy.core import (pi, oo, symbols, Rational, Integer,
                        GoldenRatio, EulerGamma, Catalan, Lambda, Dummy, Eq, nan)
from sympy.functions import (Piecewise, sin, cos, Abs, exp, ceiling, sqrt,
                             gamma, loggamma, sign, Max, Min)
from sympy.sets import Range
from sympy.logic import ITE
from sympy.codegen import For, aug_assign, Assignment
from sympy.utilities.pytest import raises
from sympy.printing.ccode import CCodePrinter, C89CodePrinter, C99CodePrinter, get_math_macros
from sympy.codegen.cfunctions import expm1, log1p, exp2, log2, fma, log10, Cbrt, hypot, Sqrt
from sympy.utilities.lambdify import implemented_function
from sympy.utilities.exceptions import SymPyDeprecationWarning
from sympy.tensor import IndexedBase, Idx
from sympy.matrices import Matrix, MatrixSymbol

from sympy import ccode

x, y, z = symbols('x,y,z')


def test_printmethod():
    class fabs(Abs):
        def _ccode(self, printer):
            return "fabs(%s)" % printer._print(self.args[0])

    assert ccode(fabs(x)) == "fabs(x)"


def test_ccode_sqrt():
    assert ccode(sqrt(x)) == "sqrt(x)"
    assert ccode(x**0.5) == "sqrt(x)"
    assert ccode(sqrt(x)) == "sqrt(x)"


def test_ccode_Pow():
    assert ccode(x**3) == "pow(x, 3)"
    assert ccode(x**(y**3)) == "pow(x, pow(y, 3))"
    g = implemented_function('g', Lambda(x, 2*x))
    assert ccode(1/(g(x)*3.5)**(x - y**x)/(x**2 + y)) == \
        "pow(3.5*2*x, -x + pow(y, x))/(pow(x, 2) + y)"
    assert ccode(x**-1.0) == '1.0/x'
    assert ccode(x**Rational(2, 3)) == 'pow(x, 2.0L/3.0L)'
    _cond_cfunc = [(lambda base, exp: exp.is_integer, "dpowi"),
                   (lambda base, exp: not exp.is_integer, "pow")]
    assert ccode(x**3, user_functions={'Pow': _cond_cfunc}) == 'dpowi(x, 3)'
    assert ccode(x**3.2, user_functions={'Pow': _cond_cfunc}) == 'pow(x, 3.2)'
    _cond_cfunc2 = [(lambda base, exp: base == 2, lambda base, exp: 'exp2(%s)' % exp),
                    (lambda base, exp: base != 2, 'pow')]
    # Related to gh-11353
    assert ccode(2**x, user_functions={'Pow': _cond_cfunc2}) == 'exp2(x)'
    assert ccode(x**2, user_functions={'Pow': _cond_cfunc2}) == 'pow(x, 2)'


def test_ccode_Max():
    # Test for gh-11926
    assert ccode(Max(x,x*x),user_functions={"Max":"my_max", "Pow":"my_pow"}) == 'my_max(x, my_pow(x, 2))'


def test_ccode_constants_mathh():
    assert ccode(exp(1)) == "M_E"
    assert ccode(pi) == "M_PI"
    assert ccode(oo, standard='c89') == "HUGE_VAL"
    assert ccode(-oo, standard='c89') == "-HUGE_VAL"
    assert ccode(oo) == "INFINITY"
    assert ccode(-oo, standard='c99') == "-INFINITY"


def test_ccode_constants_other():
    assert ccode(2*GoldenRatio) == "double const GoldenRatio = 1.61803398874989;\n2*GoldenRatio"
    assert ccode(
        2*Catalan) == "double const Catalan = 0.915965594177219;\n2*Catalan"
    assert ccode(2*EulerGamma) == "double const EulerGamma = 0.577215664901533;\n2*EulerGamma"


def test_ccode_Rational():
    assert ccode(Rational(3, 7)) == "3.0L/7.0L"
    assert ccode(Rational(18, 9)) == "2"
    assert ccode(Rational(3, -7)) == "-3.0L/7.0L"
    assert ccode(Rational(-3, -7)) == "3.0L/7.0L"
    assert ccode(x + Rational(3, 7)) == "x + 3.0L/7.0L"
    assert ccode(Rational(3, 7)*x) == "(3.0L/7.0L)*x"


def test_ccode_Integer():
    assert ccode(Integer(67)) == "67"
    assert ccode(Integer(-1)) == "-1"


def test_ccode_functions():
    assert ccode(sin(x) ** cos(x)) == "pow(sin(x), cos(x))"


def test_ccode_inline_function():
    x = symbols('x')
    g = implemented_function('g', Lambda(x, 2*x))
    assert ccode(g(x)) == "2*x"
    g = implemented_function('g', Lambda(x, 2*x/Catalan))
    assert ccode(
        g(x)) == "double const Catalan = %s;\n2*x/Catalan" % Catalan.n()
    A = IndexedBase('A')
    i = Idx('i', symbols('n', integer=True))
    g = implemented_function('g', Lambda(x, x*(1 + x)*(2 + x)))
    assert ccode(g(A[i]), assign_to=A[i]) == (
        "for (int i=0; i<n; i++){\n"
        "   A[i] = (A[i] + 1)*(A[i] + 2)*A[i];\n"
        "}"
    )


def test_ccode_exceptions():
    assert ccode(gamma(x), standard='C99') == "tgamma(x)"
    assert 'not supported in c' in ccode(gamma(x), standard='C89').lower()
    assert ccode(ceiling(x)) == "ceil(x)"
    assert ccode(Abs(x)) == "fabs(x)"
    assert ccode(gamma(x)) == "tgamma(x)"


def test_ccode_user_functions():
    x = symbols('x', integer=False)
    n = symbols('n', integer=True)
    custom_functions = {
        "ceiling": "ceil",
        "Abs": [(lambda x: not x.is_integer, "fabs"), (lambda x: x.is_integer, "abs")],
    }
    assert ccode(ceiling(x), user_functions=custom_functions) == "ceil(x)"
    assert ccode(Abs(x), user_functions=custom_functions) == "fabs(x)"
    assert ccode(Abs(n), user_functions=custom_functions) == "abs(n)"


def test_ccode_boolean():
    assert ccode(x & y) == "x && y"
    assert ccode(x | y) == "x || y"
    assert ccode(~x) == "!x"
    assert ccode(x & y & z) == "x && y && z"
    assert ccode(x | y | z) == "x || y || z"
    assert ccode((x & y) | z) == "z || x && y"
    assert ccode((x | y) & z) == "z && (x || y)"


def test_ccode_Relational():
    from sympy import Eq, Ne, Le, Lt, Gt, Ge
    assert ccode(Eq(x, y)) == "x == y"
    assert ccode(Ne(x, y)) == "x != y"
    assert ccode(Le(x, y)) == "x <= y"
    assert ccode(Lt(x, y)) == "x < y"
    assert ccode(Gt(x, y)) == "x > y"
    assert ccode(Ge(x, y)) == "x >= y"


def test_ccode_Piecewise():
    expr = Piecewise((x, x < 1), (x**2, True))
    assert ccode(expr) == (
            "((x < 1) ? (\n"
            "   x\n"
            ")\n"
            ": (\n"
            "   pow(x, 2)\n"
            "))")
    assert ccode(expr, assign_to="c") == (
            "if (x < 1) {\n"
            "   c = x;\n"
            "}\n"
            "else {\n"
            "   c = pow(x, 2);\n"
            "}")
    expr = Piecewise((x, x < 1), (x + 1, x < 2), (x**2, True))
    assert ccode(expr) == (
            "((x < 1) ? (\n"
            "   x\n"
            ")\n"
            ": ((x < 2) ? (\n"
            "   x + 1\n"
            ")\n"
            ": (\n"
            "   pow(x, 2)\n"
            ")))")
    assert ccode(expr, assign_to='c') == (
            "if (x < 1) {\n"
            "   c = x;\n"
            "}\n"
            "else if (x < 2) {\n"
            "   c = x + 1;\n"
            "}\n"
            "else {\n"
            "   c = pow(x, 2);\n"
            "}")
    # Check that Piecewise without a True (default) condition error
    expr = Piecewise((x, x < 1), (x**2, x > 1), (sin(x), x > 0))
    raises(ValueError, lambda: ccode(expr))


def test_ccode_sinc():
    from sympy import sinc
    expr = sinc(x)
    assert ccode(expr) == (
            "((x != 0) ? (\n"
            "   sin(x)/x\n"
            ")\n"
            ": (\n"
            "   1\n"
            "))")


def test_ccode_Piecewise_deep():
    p = ccode(2*Piecewise((x, x < 1), (x + 1, x < 2), (x**2, True)))
    assert p == (
            "2*((x < 1) ? (\n"
            "   x\n"
            ")\n"
            ": ((x < 2) ? (\n"
            "   x + 1\n"
            ")\n"
            ": (\n"
            "   pow(x, 2)\n"
            ")))")
    expr = x*y*z + x**2 + y**2 + Piecewise((0, x < 0.5), (1, True)) + cos(z) - 1
    assert ccode(expr) == (
            "pow(x, 2) + x*y*z + pow(y, 2) + ((x < 0.5) ? (\n"
            "   0\n"
            ")\n"
            ": (\n"
            "   1\n"
            ")) + cos(z) - 1")
    assert ccode(expr, assign_to='c') == (
            "c = pow(x, 2) + x*y*z + pow(y, 2) + ((x < 0.5) ? (\n"
            "   0\n"
            ")\n"
            ": (\n"
            "   1\n"
            ")) + cos(z) - 1;")


def test_ccode_ITE():
    expr = ITE(x < 1, x, x**2)
    assert ccode(expr) == (
            "((x < 1) ? (\n"
            "   x\n"
            ")\n"
            ": (\n"
            "   pow(x, 2)\n"
            "))")


def test_ccode_settings():
    raises(TypeError, lambda: ccode(sin(x), method="garbage"))


def test_ccode_Indexed():
    from sympy.tensor import IndexedBase, Idx
    from sympy import symbols
    s, n, m, o = symbols('s n m o', integer=True)
    i, j, k = Idx('i', n), Idx('j', m), Idx('k', o)

    x = IndexedBase('x')[j]
    A = IndexedBase('A')[i, j]
    B = IndexedBase('B')[i, j, k]

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=SymPyDeprecationWarning)
        p = CCodePrinter()
        p._not_c = set()

        assert p._print_Indexed(x) == 'x[j]'
        assert p._print_Indexed(A) == 'A[%s]' % (m*i+j)
        assert p._print_Indexed(B) == 'B[%s]' % (i*o*m+j*o+k)
        assert p._not_c == set()

        A = IndexedBase('A', shape=(5,3))[i, j]
        assert p._print_Indexed(A) == 'A[%s]' % (3*i + j)

        A = IndexedBase('A', shape=(5,3), strides='F')[i, j]
        assert ccode(A) == 'A[%s]' % (i + 5*j)

        A = IndexedBase('A', shape=(29,29), strides=(1, s), offset=o)[i, j]
        assert ccode(A) == 'A[o + s*j + i]'

        Abase = IndexedBase('A', strides=(s, m, n), offset=o)
        assert ccode(Abase[i, j, k]) == 'A[m*j + n*k + o + s*i]'
        assert ccode(Abase[2, 3, k]) == 'A[3*m + n*k + o + 2*s]'


def test_ccode_Indexed_without_looking_for_contraction():
    len_y = 5
    y = IndexedBase('y', shape=(len_y,))
    x = IndexedBase('x', shape=(len_y,))
    Dy = IndexedBase('Dy', shape=(len_y-1,))
    i = Idx('i', len_y-1)
    e=Eq(Dy[i], (y[i+1]-y[i])/(x[i+1]-x[i]))
    code0 = ccode(e.rhs, assign_to=e.lhs, contract=False)
    assert code0 == 'Dy[i] = (y[%s] - y[i])/(x[%s] - x[i]);' % (i + 1, i + 1)


def test_ccode_loops_matrix_vector():
    n, m = symbols('n m', integer=True)
    A = IndexedBase('A')
    x = IndexedBase('x')
    y = IndexedBase('y')
    i = Idx('i', m)
    j = Idx('j', n)

    s = (
        'for (int i=0; i<m; i++){\n'
        '   y[i] = 0;\n'
        '}\n'
        'for (int i=0; i<m; i++){\n'
        '   for (int j=0; j<n; j++){\n'
        '      y[i] = A[%s]*x[j] + y[i];\n' % (i*n + j) +\
        '   }\n'
        '}'
    )
    assert ccode(A[i, j]*x[j], assign_to=y[i]) == s


def test_dummy_loops():
    i, m = symbols('i m', integer=True, cls=Dummy)
    x = IndexedBase('x')
    y = IndexedBase('y')
    i = Idx(i, m)

    expected = (
        'for (int i_%(icount)i=0; i_%(icount)i<m_%(mcount)i; i_%(icount)i++){\n'
        '   y[i_%(icount)i] = x[i_%(icount)i];\n'
        '}'
    ) % {'icount': i.label.dummy_index, 'mcount': m.dummy_index}

    assert ccode(x[i], assign_to=y[i]) == expected


def test_ccode_loops_add():
    from sympy.tensor import IndexedBase, Idx
    from sympy import symbols
    n, m = symbols('n m', integer=True)
    A = IndexedBase('A')
    x = IndexedBase('x')
    y = IndexedBase('y')
    z = IndexedBase('z')
    i = Idx('i', m)
    j = Idx('j', n)

    s = (
        'for (int i=0; i<m; i++){\n'
        '   y[i] = x[i] + z[i];\n'
        '}\n'
        'for (int i=0; i<m; i++){\n'
        '   for (int j=0; j<n; j++){\n'
        '      y[i] = A[%s]*x[j] + y[i];\n' % (i*n + j) +\
        '   }\n'
        '}'
    )
    assert ccode(A[i, j]*x[j] + x[i] + z[i], assign_to=y[i]) == s


def test_ccode_loops_multiple_contractions():
    from sympy.tensor import IndexedBase, Idx
    from sympy import symbols
    n, m, o, p = symbols('n m o p', integer=True)
    a = IndexedBase('a')
    b = IndexedBase('b')
    y = IndexedBase('y')
    i = Idx('i', m)
    j = Idx('j', n)
    k = Idx('k', o)
    l = Idx('l', p)

    s = (
        'for (int i=0; i<m; i++){\n'
        '   y[i] = 0;\n'
        '}\n'
        'for (int i=0; i<m; i++){\n'
        '   for (int j=0; j<n; j++){\n'
        '      for (int k=0; k<o; k++){\n'
        '         for (int l=0; l<p; l++){\n'
        '            y[i] = a[%s]*b[%s] + y[i];\n' % (i*n*o*p + j*o*p + k*p + l, j*o*p + k*p + l) +\
        '         }\n'
        '      }\n'
        '   }\n'
        '}'
    )
    assert ccode(b[j, k, l]*a[i, j, k, l], assign_to=y[i]) == s


def test_ccode_loops_addfactor():
    from sympy.tensor import IndexedBase, Idx
    from sympy import symbols
    n, m, o, p = symbols('n m o p', integer=True)
    a = IndexedBase('a')
    b = IndexedBase('b')
    c = IndexedBase('c')
    y = IndexedBase('y')
    i = Idx('i', m)
    j = Idx('j', n)
    k = Idx('k', o)
    l = Idx('l', p)

    s = (
        'for (int i=0; i<m; i++){\n'
        '   y[i] = 0;\n'
        '}\n'
        'for (int i=0; i<m; i++){\n'
        '   for (int j=0; j<n; j++){\n'
        '      for (int k=0; k<o; k++){\n'
        '         for (int l=0; l<p; l++){\n'
        '            y[i] = (a[%s] + b[%s])*c[%s] + y[i];\n' % (i*n*o*p + j*o*p + k*p + l, i*n*o*p + j*o*p + k*p + l, j*o*p + k*p + l) +\
        '         }\n'
        '      }\n'
        '   }\n'
        '}'
    )
    assert ccode((a[i, j, k, l] + b[i, j, k, l])*c[j, k, l], assign_to=y[i]) == s


def test_ccode_loops_multiple_terms():
    from sympy.tensor import IndexedBase, Idx
    from sympy import symbols
    n, m, o, p = symbols('n m o p', integer=True)
    a = IndexedBase('a')
    b = IndexedBase('b')
    c = IndexedBase('c')
    y = IndexedBase('y')
    i = Idx('i', m)
    j = Idx('j', n)
    k = Idx('k', o)

    s0 = (
        'for (int i=0; i<m; i++){\n'
        '   y[i] = 0;\n'
        '}\n'
    )
    s1 = (
        'for (int i=0; i<m; i++){\n'
        '   for (int j=0; j<n; j++){\n'
        '      for (int k=0; k<o; k++){\n'
        '         y[i] = b[j]*b[k]*c[%s] + y[i];\n' % (i*n*o + j*o + k) +\
        '      }\n'
        '   }\n'
        '}\n'
    )
    s2 = (
        'for (int i=0; i<m; i++){\n'
        '   for (int k=0; k<o; k++){\n'
        '      y[i] = a[%s]*b[k] + y[i];\n' % (i*o + k) +\
        '   }\n'
        '}\n'
    )
    s3 = (
        'for (int i=0; i<m; i++){\n'
        '   for (int j=0; j<n; j++){\n'
        '      y[i] = a[%s]*b[j] + y[i];\n' % (i*n + j) +\
        '   }\n'
        '}\n'
    )
    c = ccode(b[j]*a[i, j] + b[k]*a[i, k] + b[j]*b[k]*c[i, j, k], assign_to=y[i])
    assert (c == s0 + s1 + s2 + s3[:-1] or
            c == s0 + s1 + s3 + s2[:-1] or
            c == s0 + s2 + s1 + s3[:-1] or
            c == s0 + s2 + s3 + s1[:-1] or
            c == s0 + s3 + s1 + s2[:-1] or
            c == s0 + s3 + s2 + s1[:-1])


def test_dereference_printing():
    expr = x + y + sin(z) + z
    assert ccode(expr, dereference=[z]) == "x + y + (*z) + sin((*z))"


def test_Matrix_printing():
    # Test returning a Matrix
    mat = Matrix([x*y, Piecewise((2 + x, y>0), (y, True)), sin(z)])
    A = MatrixSymbol('A', 3, 1)
    assert ccode(mat, A) == (
        "A[0] = x*y;\n"
        "if (y > 0) {\n"
        "   A[1] = x + 2;\n"
        "}\n"
        "else {\n"
        "   A[1] = y;\n"
        "}\n"
        "A[2] = sin(z);")
    # Test using MatrixElements in expressions
    expr = Piecewise((2*A[2, 0], x > 0), (A[2, 0], True)) + sin(A[1, 0]) + A[0, 0]
    assert ccode(expr) == (
        "((x > 0) ? (\n"
        "   2*A[2]\n"
        ")\n"
        ": (\n"
        "   A[2]\n"
        ")) + sin(A[1]) + A[0]")
    # Test using MatrixElements in a Matrix
    q = MatrixSymbol('q', 5, 1)
    M = MatrixSymbol('M', 3, 3)
    m = Matrix([[sin(q[1,0]), 0, cos(q[2,0])],
        [q[1,0] + q[2,0], q[3, 0], 5],
        [2*q[4, 0]/q[1,0], sqrt(q[0,0]) + 4, 0]])
    assert ccode(m, M) == (
        "M[0] = sin(q[1]);\n"
        "M[1] = 0;\n"
        "M[2] = cos(q[2]);\n"
        "M[3] = q[1] + q[2];\n"
        "M[4] = q[3];\n"
        "M[5] = 5;\n"
        "M[6] = 2*q[4]/q[1];\n"
        "M[7] = sqrt(q[0]) + 4;\n"
        "M[8] = 0;")


def test_ccode_reserved_words():
    x, y = symbols('x, if')
    with raises(ValueError):
        ccode(y**2, error_on_reserved=True, standard='C99')
    assert ccode(y**2) == 'pow(if_, 2)'
    assert ccode(x * y**2, dereference=[y]) == 'pow((*if_), 2)*x'
    assert ccode(y**2, reserved_word_suffix='_unreserved') == 'pow(if_unreserved, 2)'


def test_ccode_sign():
    expr1, ref1 = sign(x) * y, 'y*(((x) > 0) - ((x) < 0))'
    expr2, ref2 = sign(cos(x)), '(((cos(x)) > 0) - ((cos(x)) < 0))'
    expr3, ref3 = sign(2 * x + x**2) * x + x**2, 'pow(x, 2) + x*(((pow(x, 2) + 2*x) > 0) - ((pow(x, 2) + 2*x) < 0))'
    assert ccode(expr1) == ref1
    assert ccode(expr1, 'z') == 'z = %s;' % ref1
    assert ccode(expr2) == ref2
    assert ccode(expr3) == ref3

def test_ccode_Assignment():
    assert ccode(Assignment(x, y + z)) == 'x = y + z;'
    assert ccode(aug_assign(x, '+', y + z)) == 'x += y + z;'


def test_ccode_For():
    f = For(x, Range(0, 10, 2), [aug_assign(y, '*', x)])
    assert ccode(f) == ("for (x = 0; x < 10; x += 2) {\n"
                        "   y *= x;\n"
                        "}")

def test_ccode_Max_Min():
    assert ccode(Max(x, 0), standard='C89') == '((0 > x) ? 0 : x)'
    assert ccode(Max(x, 0), standard='C99') == 'fmax(0, x)'
    assert ccode(Min(x, 0, sqrt(x)), standard='c89') == (
        '((0 < ((x < sqrt(x)) ? x : sqrt(x))) ? 0 : ((x < sqrt(x)) ? x : sqrt(x)))'
    )

def test_ccode_standard():
    assert ccode(expm1(x), standard='c99') == 'expm1(x)'
    assert ccode(nan, standard='c99') == 'NAN'
    assert ccode(float('nan'), standard='c99') == 'NAN'


def test_CCodePrinter():
    with warnings.catch_warnings():
        warnings.filterwarnings("error", category=SymPyDeprecationWarning)
        with raises(SymPyDeprecationWarning):
            CCodePrinter()
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=SymPyDeprecationWarning)
        assert CCodePrinter().language == 'C'


def test_C89CodePrinter():
    c89printer = C89CodePrinter()
    assert c89printer.language == 'C'
    assert c89printer.standard == 'C89'
    assert 'void' in c89printer.reserved_words
    assert 'template' not in c89printer.reserved_words


def test_C99CodePrinter():
    assert C99CodePrinter().doprint(expm1(x)) == 'expm1(x)'
    assert C99CodePrinter().doprint(log1p(x)) == 'log1p(x)'
    assert C99CodePrinter().doprint(exp2(x)) == 'exp2(x)'
    assert C99CodePrinter().doprint(log2(x)) == 'log2(x)'
    assert C99CodePrinter().doprint(fma(x, y, -z)) == 'fma(x, y, -z)'
    assert C99CodePrinter().doprint(log10(x)) == 'log10(x)'
    assert C99CodePrinter().doprint(Cbrt(x)) == 'cbrt(x)'  # note Cbrt due to cbrt already taken.
    assert C99CodePrinter().doprint(hypot(x, y)) == 'hypot(x, y)'
    assert C99CodePrinter().doprint(loggamma(x)) == 'lgamma(x)'
    assert C99CodePrinter().doprint(Max(x, 3, x**2)) == 'fmax(3, fmax(x, pow(x, 2)))'
    assert C99CodePrinter().doprint(Min(x, 3)) == 'fmin(3, x)'
    c99printer = C99CodePrinter()
    assert c99printer.language == 'C'
    assert c99printer.standard == 'C99'
    assert 'restrict' in c99printer.reserved_words
    assert 'using' not in c99printer.reserved_words


def test_get_math_macros():
    macros = get_math_macros()
    assert macros[exp(1)] == 'M_E'
    assert macros[1/Sqrt(2)] == 'M_SQRT1_2'


def test_MatrixElement_printing():
    # test cases for issue #11821
    A = MatrixSymbol("A", 1, 3)
    B = MatrixSymbol("B", 1, 3)
    C = MatrixSymbol("C", 1, 3)

    assert(ccode(A[0, 0]) == "A[0]")
    assert(ccode(3 * A[0, 0]) == "3*A[0]")

    F = C[0, 0].subs(C, A - B)
    assert(ccode(F) == "((-1)*B + A)[0]")


def test_subclass_CCodePrinter():
    # issue gh-12687
    class MySubClass(CCodePrinter):
        pass
