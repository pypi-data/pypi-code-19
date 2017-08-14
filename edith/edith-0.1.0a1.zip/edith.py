class InvalidCoords(IndexError):
    pass


class Edition(object):
    def __eq__(self, other):
        if not isinstance(other, Edition):
            raise TypeError()
        return self.__class__ is other.__class__

    @staticmethod
    def Apply(src, path, debug=False):
        def iter_chain(chain, deletes=False):
            d = 1 if not deletes else -1
            for edition in chain[::d]:
                if isinstance(edition, Deletion) == deletes:
                    yield edition

        def debug_me(f):
            def new_f(ed, st):
                result = f(ed, st)
                if debug:
                    print ed, ':', st, '->', result
                return result
            return new_f

        @debug_me
        def run(edition, state):
            return edition.apply(state)

        current = src
        for order in [True, False]:
            for edit in iter_chain(path, order):
                current = run(edit, current)
        return current

    def wrap_element(self, element, context):
        return [element] if isinstance(context, list) else element


class Sustitution(Edition):
    def __init__(self, x, what):
        self.what = what
        self.x = x

    def __eq__(self, other):
        return super(Sustitution, self).__eq__(other) and (self.x == other.x) and (self.what == other.what)

    def __str__(self):
        return 'sust-%d-%c' % (self.x, self.what)

    def __repr__(self):
        return '\\S%d%c' % (self.x, self.what)

    def apply(self, on):
        what = self.wrap_element(self.what, on)
        return on[:self.x - 1] + what + on[self.x:]


class Insertion(Edition):
    def __init__(self, x, what):
        self.what = what
        self.x = x

    def __eq__(self, other):
        return super(Insertion, self).__eq__(other) and (self.x == other.x) and (self.what == other.what)

    def __str__(self):
        return 'inst-%d-%c' % (self.x, self.what)

    def __repr__(self):
        return '|I%d%c' % (self.x, self.what)

    def apply(self, on):
        what = self.wrap_element(self.what, on)
        return on[:self.x] + what + on[self.x:]


class Deletion(Edition):
    def __init__(self, x):
        self.x = x

    def __eq__(self, other):
        return super(Deletion, self).__eq__(other) and (self.x == other.x)

    def __str__(self):
        return 'del-%d' % self.x

    def __repr__(self):
        return '-D%d ' % self.x

    def apply(self, on):
        on = on[:self.x - 1] + on[self.x:]
        return on


class D2Array:
    def __init__(self, x, y, default=None):
        self.data = {}
        self.size_x = x
        self.size_y = y
        self.default = default

    def check_coords(self, x, y):
        def check(value, max_value):
            if (value < 0) or (value >= max_value):
                raise InvalidCoords("(%d, %d)" % (x, y))

        check(x, self.size_x)
        check(y, self.size_y)

    def get(self, x, y):
        self.check_coords(x, y)
        if self.default is None:
            return self.data[(x, y)]
        return self.data.setdefault((x, y), self.default)

    def put(self, x, y, value):
        self.check_coords(x, y)
        self.data[(x, y)] = value

    def dump(self, src='', tgt='', full=True):
        def full_format(xx, yy):
            ops = self.get(xx, yy)
            if len(ops) > 0:
                return repr(ops[-1])
            return '*[-]'

        size = 1 if not full else 5

        print
        tgt = ' ' + tgt
        if tgt == ' ':
            tgt = ' ' * self.size_y
        sep = ' ' * size
        if src != '':
            print sep.join(list('  ' + src))

        for y in xrange(self.size_y):
            print sep[:-1] + tgt[y],
            for x in xrange(self.size_x):
                if full:
                    print '%d%s' % (len(self.get(x, y)), full_format(x, y)),
                else:
                    print len(self.get(x, y)),
            print


class Distance:
    def __init__(self, fromstr, tostr, cmp_op=lambda x, y:x==y):
        self.tostr = tostr
        self.fromstr = fromstr
        self.d2 = None
        self.cmp_op = cmp_op

    def setup_op_matrix(self, x, y):
        prev_x = lambda d, idx: d.get(0, idx - 1)
        prev_y = lambda d, idx: d.get(idx - 1, 0)
        ar2d = D2Array(x, y, [])
        for i in xrange(1, x):
            ar2d.put(i, 0, prev_y(ar2d, i) + [Deletion(i)])
        for i in xrange(1, y):
            ar2d.put(0, i, prev_x(ar2d, i) + [Insertion(i - 1, self.tostr[i - 1])])
        return ar2d

    def calc(self):
        m = len(self.fromstr) + 1
        n = len(self.tostr) + 1
        self.d2 = self.setup_op_matrix(m, n)

        for j in range(1, n):  # to / Y
            for i in range(1, m):  # from / X
                if self.cmp_op(self.fromstr[i - 1], self.tostr[j - 1]):
                    temp = self.d2.get(i - 1, j - 1)
                else:
                    deletion = self.d2.get(i - 1, j) + [Deletion(i)]  # -
                    insertion = self.d2.get(i, j - 1) + [Insertion(j - 1, self.tostr[j - 1])]  # |
                    sustitution = self.d2.get(i - 1, j - 1) + [Sustitution(j, self.tostr[j - 1])]  # \
                    temp = min(deletion, insertion, sustitution, key=lambda x: len(x))
                self.d2.put(i, j, temp)
        return len(self.d2.get(m - 1, n - 1))

    def dump(self):
        show = isinstance(self.fromstr, str) and isinstance(self.tostr, str)
        if show:
            self.d2.dump(self.fromstr, self.tostr)
        else:
            self.d2.dump()

    def editpath(self):
        m = len(self.fromstr) + 1
        n = len(self.tostr) + 1
        return self.d2.get(m - 1, n - 1)


CASES = [
    ("kitten", "sitting", 3),
    ("Saturday", "Sunday", 3),
    ("Saturday", " Saturday", 1),
    (" Saturday", "Saturday", 1),
    (" Saturday", "urday", 4),
    (['S', 'a', 't', 'u', 'r', 'd', 'a', 'y'], [' ', 'S', 'a', 't', 'u', 'r', 'd', 'a', 'y'], 1),
    # base
    ('a', 'a', 0),
    # insert
    ('', 'a', 1),
    ('a', 'ab', 1),
    ('ababc', 'abcabc', 1),
    # sustitutions
    ('a', 'b', 1),
    ('aa', 'ab', 1),
    ('abxabc', 'abcabc', 1),
    # deletions
    ('aba', 'aa', 1),
    ('ab', 'a', 1),
    ('ba', 'a', 1),
]


def test_cases():
    for src, tgt, length in CASES:
        yield check_distance, src, tgt, length
        yield check_distance, tgt, src, length


def check_distance(src, tgt, length):
    dst = Distance(src, tgt)
    calc = dst.calc()
    path = dst.editpath()
    assert calc == length
    dst.dump()
    print
    print path
    for edition in dst.editpath():
        assert isinstance(edition, Edition), "edition %r is not an Edition!" % edition
    assert Edition.Apply(src, path) == tgt
