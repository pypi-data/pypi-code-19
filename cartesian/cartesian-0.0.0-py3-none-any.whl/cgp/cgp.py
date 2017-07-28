import itertools
from operator import attrgetter
from collections import namedtuple

from sklearn.base import TransformerMixin
from sklearn.utils.validation import check_random_state

from .util import make_it


class Primitive(object):
    def __init__(self, name, function, arity):
        self.name = name
        self.function = function
        self.arity = arity


class Constant(Primitive):
    arity = 0
    def __init__(self, name, function=None):
        self.name = name
        self.function = function


class ERC(Primitive):
    arity = 0


class Terminal(Primitive):
    arity = 0
    def __init__(self, name):
        self.name = name


PrimitiveSet = namedtuple("PrimitiveSet", "operators terminals max_arity mapping")


def create_pset(primitives):
    operators = [p for p in primitives if p.arity > 0]
    terminals = [p for p in primitives if p.arity == 0]
    max_arity = max(operators, key=attrgetter("arity")).arity

    mapping = {i: prim for i, prim in enumerate(sorted(terminals, key=attrgetter("name")) \
                                              + sorted(operators, key=attrgetter("name")))}

    return PrimitiveSet(operators=operators, terminals=terminals,
                        max_arity=max_arity, mapping=mapping)


class Cartesian(TransformerMixin):
    pset = None
    def __init__(self, code, outputs):
        self.inputs = list(range(len(self.pset.terminals)))
        self.code = code
        self.outputs = outputs
        self._flat = None

    def __getitem__(self, index):
        if self._flat is None:
            self._flat = self.inputs + sum(self.code, []) + self.outputs
        return self._flat[index]

    def fit(self, x, y=None, **fit_params):
        self._transform = compile(self)
        self.fit_params = fit_params
        return self

    def transform(self, x, y=None):
        return self._transform(*x.T)

    @classmethod
    def create(cls, n_in, n_columns, n_rows, n_back, n_out, random_state=None):
        random_state = check_random_state(random_state)

        operator_keys = list(range(len(cls.pset.terminals), max(cls.pset.mapping) + 1))
        code = []
        for i in range(n_columns):
            column = []
            for j in range(n_rows):
                min_input = max(0, (i-n_back)*n_rows) + len(cls.pset.terminals)
                max_input = i * n_rows - 1 + len(cls.pset.terminals)
                in_ = list(range(min_input, max_input)) + list(range(0, len(cls.pset.terminals)))
                gene = [random_state.choice(operator_keys)] + [random_state.choice(in_) for _ in range(cls.pset.max_arity)]
                column.append(gene)
            code.append(column)
        outputs = [random_state.randint(0, n_columns*n_rows + n_in) for _ in range(n_out)]
        return cls(code, outputs)


def to_polish(c, return_args=True):
    primitives = c.pset.mapping

    used_arguments = set()

    def h(g):
        gene = make_it(c[g])
        primitive = primitives[next(gene)]

        if primitive.arity == 0:
            if isinstance(primitive, Terminal):
                used_arguments.add(primitive)
            return primitive.name
        else:
            return "{}({})".format(primitive.name,
                                   ", ".join(h(a) for a, _ in zip(gene, range(primitive.arity))))

    polish = [h(o) for o in c.outputs]

    if return_args:
        return polish, used_arguments
    else:
        return polish


def boilerplate(c, used_arguments=()):
    mapping = c.pset.mapping
    if used_arguments:
        index = sorted([k for (k, v) in mapping.items() if v in used_arguments])
        args = [mapping[i] for i in index]
    else:
        args = [mapping[i] for i in c.inputs]
    args = [a for a in args if not isinstance(a, Constant)] + [a for a in args if isinstance(a, Constant)]
    return "lambda " + ", ".join(a.name for a in args) + ": "


def compile(c):
    code_, args = to_polish(c, return_args=True)
    print(args)
    bp = boilerplate(c, used_arguments=args)
    code = "(" + ", ".join(code_) + ")" if len(code_) > 1 else code_[0]
    return eval(bp + code, context)


if __name__ == '__main__':
    import operator
    import random
    terminals = [Terminal("x_0")]
    operators = [Primitive("mul", operator.mul, 2),
                 Primitive("add", operator.add, 2),
                 ERC]

    pset = create_pset(terminals + operators)

    Cartesian.pset = pset
    individual = Cartesian.create(1, 3, 3, 1, 2)
    print(individual.inputs)
    print(to_polish(individual))
    print(boilerplate(individual, used_arguments=terminals))
