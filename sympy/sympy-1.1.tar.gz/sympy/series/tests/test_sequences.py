from sympy import (S, Tuple, symbols, Interval, EmptySequence, oo, SeqPer,
                   SeqFormula, sequence, SeqAdd, SeqMul, Indexed, Idx, sqrt,
                   fibonacci)
from sympy.series.sequences import SeqExpr, SeqExprOp
from sympy.utilities.pytest import raises

x, y, z = symbols('x y z')
n, m = symbols('n m')


def test_EmptySequence():
    assert isinstance(S.EmptySequence, EmptySequence)

    assert S.EmptySequence.interval is S.EmptySet
    assert S.EmptySequence.length is S.Zero

    assert list(S.EmptySequence) == []


def test_SeqExpr():
    s = SeqExpr((1, n, y), (x, 0, 10))

    assert isinstance(s, SeqExpr)
    assert s.gen == (1, n, y)
    assert s.interval == Interval(0, 10)
    assert s.start == 0
    assert s.stop == 10
    assert s.length == 11
    assert s.variables == (x,)

    assert SeqExpr((1, 2, 3), (x, 0, oo)).length is oo


def test_SeqPer():
    s = SeqPer((1, n, 3), (x, 0, 5))

    assert isinstance(s, SeqPer)
    assert s.periodical == Tuple(1, n, 3)
    assert s.period == 3
    assert s.coeff(3) == 1
    assert s.free_symbols == {n}

    assert list(s) == [1, n, 3, 1, n, 3]
    assert s[:] == [1, n, 3, 1, n, 3]
    assert SeqPer((1, n, 3), (x, -oo, 0))[0:6] == [1, n, 3, 1, n, 3]

    raises(ValueError, lambda: SeqPer((1, 2, 3), (0, 1, 2)))
    raises(ValueError, lambda: SeqPer((1, 2, 3), (x, -oo, oo)))
    raises(ValueError, lambda: SeqPer(n**2, (0, oo)))

    assert SeqPer((n, n**2, n**3), (m, 0, oo))[:6] == \
        [n, n**2, n**3, n, n**2, n**3]
    assert SeqPer((n, n**2, n**3), (n, 0, oo))[:6] == [0, 1, 8, 3, 16, 125]
    assert SeqPer((n, m), (n, 0, oo))[:6] == [0, m, 2, m, 4, m]


def test_SeqFormula():
    s = SeqFormula(n**2, (n, 0, 5))

    assert isinstance(s, SeqFormula)
    assert s.formula == n**2
    assert s.coeff(3) == 9

    assert list(s) == [i**2 for i in range(6)]
    assert s[:] == [i**2 for i in range(6)]
    assert SeqFormula(n**2, (n, -oo, 0))[0:6] == [i**2 for i in range(6)]

    assert SeqFormula(n**2, (0, oo)) == SeqFormula(n**2, (n, 0, oo))

    assert SeqFormula(n**2, (0, m)).subs(m, x) == SeqFormula(n**2, (0, x))
    assert SeqFormula(m*n**2, (n, 0, oo)).subs(m, x) == \
        SeqFormula(x*n**2, (n, 0, oo))

    raises(ValueError, lambda: SeqFormula(n**2, (0, 1, 2)))
    raises(ValueError, lambda: SeqFormula(n**2, (n, -oo, oo)))
    raises(ValueError, lambda: SeqFormula(m*n**2, (0, oo)))


def test_sequence():
    form = SeqFormula(n**2, (n, 0, 5))
    per = SeqPer((1, 2, 3), (n, 0, 5))
    inter = SeqFormula(n**2)

    assert sequence(n**2, (n, 0, 5)) == form
    assert sequence((1, 2, 3), (n, 0, 5)) == per
    assert sequence(n**2) == inter


def test_SeqExprOp():
    form = SeqFormula(n**2, (n, 0, 10))
    per = SeqPer((1, 2, 3), (m, 5, 10))

    s = SeqExprOp(form, per)
    assert s.gen == (n**2, (1, 2, 3))
    assert s.interval == Interval(5, 10)
    assert s.start == 5
    assert s.stop == 10
    assert s.length == 6
    assert s.variables == (n, m)


def test_SeqAdd():
    per = SeqPer((1, 2, 3), (n, 0, oo))
    form = SeqFormula(n**2)

    per_bou = SeqPer((1, 2), (n, 1, 5))
    form_bou = SeqFormula(n**2, (6, 10))
    form_bou2 = SeqFormula(n**2, (1, 5))

    assert SeqAdd() == S.EmptySequence
    assert SeqAdd(S.EmptySequence) == S.EmptySequence
    assert SeqAdd(per) == per
    assert SeqAdd(per, S.EmptySequence) == per
    assert SeqAdd(per_bou, form_bou) == S.EmptySequence

    s = SeqAdd(per_bou, form_bou2, evaluate=False)
    assert s.args == (form_bou2, per_bou)
    assert s[:] == [2, 6, 10, 18, 26]
    assert list(s) == [2, 6, 10, 18, 26]

    assert isinstance(SeqAdd(per, per_bou, evaluate=False), SeqAdd)

    s1 = SeqAdd(per, per_bou)
    assert isinstance(s1, SeqPer)
    assert s1 == SeqPer((2, 4, 4, 3, 3, 5), (n, 1, 5))
    s2 = SeqAdd(form, form_bou)
    assert isinstance(s2, SeqFormula)
    assert s2 == SeqFormula(2*n**2, (6, 10))

    assert SeqAdd(form, form_bou, per) == \
        SeqAdd(per, SeqFormula(2*n**2, (6, 10)))
    assert SeqAdd(form, SeqAdd(form_bou, per)) == \
        SeqAdd(per, SeqFormula(2*n**2, (6, 10)))
    assert SeqAdd(per, SeqAdd(form, form_bou), evaluate=False) == \
        SeqAdd(per, SeqFormula(2*n**2, (6, 10)))

    assert SeqAdd(SeqPer((1, 2), (n, 0, oo)), SeqPer((1, 2), (m, 0, oo))) == \
        SeqPer((2, 4), (n, 0, oo))


def test_SeqMul():
    per = SeqPer((1, 2, 3), (n, 0, oo))
    form = SeqFormula(n**2)

    per_bou = SeqPer((1, 2), (n, 1, 5))
    form_bou = SeqFormula(n**2, (n, 6, 10))
    form_bou2 = SeqFormula(n**2, (1, 5))

    assert SeqMul() == S.EmptySequence
    assert SeqMul(S.EmptySequence) == S.EmptySequence
    assert SeqMul(per) == per
    assert SeqMul(per, S.EmptySequence) == S.EmptySequence
    assert SeqMul(per_bou, form_bou) == S.EmptySequence

    s = SeqMul(per_bou, form_bou2, evaluate=False)
    assert s.args == (form_bou2, per_bou)
    assert s[:] == [1, 8, 9, 32, 25]
    assert list(s) == [1, 8, 9, 32, 25]

    assert isinstance(SeqMul(per, per_bou, evaluate=False), SeqMul)

    s1 = SeqMul(per, per_bou)
    assert isinstance(s1, SeqPer)
    assert s1 == SeqPer((1, 4, 3, 2, 2, 6), (n, 1, 5))
    s2 = SeqMul(form, form_bou)
    assert isinstance(s2, SeqFormula)
    assert s2 == SeqFormula(n**4, (6, 10))

    assert SeqMul(form, form_bou, per) == \
        SeqMul(per, SeqFormula(n**4, (6, 10)))
    assert SeqMul(form, SeqMul(form_bou, per)) == \
        SeqMul(per, SeqFormula(n**4, (6, 10)))
    assert SeqMul(per, SeqMul(form, form_bou2,
                              evaluate=False), evaluate=False) == \
        SeqMul(form, per, form_bou2, evaluate=False)

    assert SeqMul(SeqPer((1, 2), (n, 0, oo)), SeqPer((1, 2), (n, 0, oo))) == \
        SeqPer((1, 4), (n, 0, oo))


def test_add():
    per = SeqPer((1, 2), (n, 0, oo))
    form = SeqFormula(n**2)

    assert per + (SeqPer((2, 3))) == SeqPer((3, 5), (n, 0, oo))
    assert form + SeqFormula(n**3) == SeqFormula(n**2 + n**3)

    assert per + form == SeqAdd(per, form)

    raises(TypeError, lambda: per + n)
    raises(TypeError, lambda: n + per)


def test_sub():
    per = SeqPer((1, 2), (n, 0, oo))
    form = SeqFormula(n**2)

    assert per - (SeqPer((2, 3))) == SeqPer((-1, -1), (n, 0, oo))
    assert form - (SeqFormula(n**3)) == SeqFormula(n**2 - n**3)

    assert per - form == SeqAdd(per, -form)

    raises(TypeError, lambda: per - n)
    raises(TypeError, lambda: n - per)


def test_mul__coeff_mul():
    assert SeqPer((1, 2), (n, 0, oo)).coeff_mul(2) == SeqPer((2, 4), (n, 0, oo))
    assert SeqFormula(n**2).coeff_mul(2) == SeqFormula(2*n**2)
    assert S.EmptySequence.coeff_mul(100) == S.EmptySequence

    assert SeqPer((1, 2), (n, 0, oo)) * (SeqPer((2, 3))) == \
        SeqPer((2, 6), (n, 0, oo))
    assert SeqFormula(n**2) * SeqFormula(n**3) == SeqFormula(n**5)

    assert S.EmptySequence * SeqFormula(n**2) == S.EmptySequence
    assert SeqFormula(n**2) * S.EmptySequence == S.EmptySequence

    raises(TypeError, lambda: sequence(n**2) * n)
    raises(TypeError, lambda: n * sequence(n**2))


def test_neg():
    assert -SeqPer((1, -2), (n, 0, oo)) == SeqPer((-1, 2), (n, 0, oo))
    assert -SeqFormula(n**2) == SeqFormula(-n**2)


def test_operations():
    per = SeqPer((1, 2), (n, 0, oo))
    per2 = SeqPer((2, 4), (n, 0, oo))
    form = SeqFormula(n**2)
    form2 = SeqFormula(n**3)

    assert per + form + form2 == SeqAdd(per, form, form2)
    assert per + form - form2 == SeqAdd(per, form, -form2)
    assert per + form - S.EmptySequence == SeqAdd(per, form)
    assert per + per2 + form == SeqAdd(SeqPer((3, 6), (n, 0, oo)), form)
    assert S.EmptySequence - per == -per
    assert form + form == SeqFormula(2*n**2)

    assert per * form * form2 == SeqMul(per, form, form2)
    assert form * form == SeqFormula(n**4)
    assert form * -form == SeqFormula(-n**4)

    assert form * (per + form2) == SeqMul(form, SeqAdd(per, form2))
    assert form * (per + per) == SeqMul(form, per2)

    assert form.coeff_mul(m) == SeqFormula(m*n**2, (n, 0, oo))
    assert per.coeff_mul(m) == SeqPer((m, 2*m), (n, 0, oo))


def test_Idx_limits():
    i = symbols('i', cls=Idx)
    r = Indexed('r', i)

    assert SeqFormula(r, (i, 0, 5))[:] == [r.subs(i, j) for j in range(6)]
    assert SeqPer((1, 2), (i, 0, 5))[:] == [1, 2, 1, 2, 1, 2]

def test_find_linear_recurrence():
    assert sequence((0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55), \
    (n, 0, 10)).find_linear_recurrence(11) == [1, 1]
    assert sequence((1, 2, 4, 7, 28, 128, 582, 2745, 13021, 61699, 292521, \
    1387138), (n, 0, 11)).find_linear_recurrence(12) == [5, -2, 6, -11]
    assert sequence(x*n**3+y*n, (n, 0, oo)).find_linear_recurrence(10) \
    == [4, -6, 4, -1]
    assert sequence(x**n, (n,0,20)).find_linear_recurrence(21) == [x]
    assert sequence((1,2,3)).find_linear_recurrence(10, 5) == [0, 0, 1]
    assert sequence(((1 + sqrt(5))/2)**n + \
    (-(1 + sqrt(5))/2)**(-n)).find_linear_recurrence(10) == [1, 1]
    assert sequence(x*((1 + sqrt(5))/2)**n + y*(-(1 + sqrt(5))/2)**(-n), \
    (n,0,oo)).find_linear_recurrence(10) == [1, 1]
    assert sequence((1,2,3,4,6),(n, 0, 4)).find_linear_recurrence(5) == []
    assert sequence((2,3,4,5,6,79),(n, 0, 5)).find_linear_recurrence(6,gfvar=x) \
    == ([], None)
    assert sequence((2,3,4,5,8,30),(n, 0, 5)).find_linear_recurrence(6,gfvar=x) \
    == ([19/2, -20, 27/2], (-31*x**2 + 32*x - 4)/(27*x**3 - 40*x**2 + 19*x -2))
    assert sequence(fibonacci(n)).find_linear_recurrence(30,gfvar=x) \
    == ([1, 1], -x/(x**2 + x - 1))
