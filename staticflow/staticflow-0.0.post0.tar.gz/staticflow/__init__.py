import itertools
import redbaron
import sys
import warnings


PY3 = sys.version_info[0] == 3


if PY3:
    irange = range
    itervalues = lambda d: d.values()
    int_types = int,
    unicode_ = str
    text = str
else:
    irange = xrange  # noqa: F821
    itervalues = lambda d: d.itervalues()
    int_types = int, long  # noqa: F821
    unicode_ = unicode  # noqa: F821
    text = str, unicode_


def utf8(s):
    if isinstance(s, unicode_):
        return s
    elif isinstance(s, bytes):
        return s.decode('utf-8')
    else:
        raise TypeError("Got %r instead of str or unicode" % type(s))


def default(dct, key, cstr):
    try:
        return dct[key]
    except KeyError:
        value = cstr()
        dct[key] = value
        return value


# All the nodes. Used to assert that I listed them all here
all_nodes = set(n for n in dir(redbaron.nodes)
                if 'A' <= n[0] <= 'Z' and n.endswith('Node'))

# Recurse on those nodes, they can contain assigments in the same scope
do_enter = set([
    'AssociativeParenthesisNode',
    'AtomtrailersNode',
    'BinaryNode',
    'BinaryOperatorNode',
    'BinaryRawStringNode',
    'BinaryStringNode',
    'BooleanOperatorNode',
    'BreakNode',
    'CallArgumentNode',
    'CallNode',
    'ClassNode',
    'CodeBlockNode',
    'CommaNode',
    'CommentNode',
    'ComparisonNode',
    'ComparisonOperatorNode',
    'ComplexNode',
    'ComprehensionIfNode',
    'ComprehensionLoopNode',
    'ContinueNode',
    'DecoratorNode',
    'DefArgumentNode',
    'DefNode',
    'DelNode',
    'DictArgumentNode',
    'DictComprehensionNode',
    'DictNode',
    'DictitemNode',
    'DotNode',
    'DottedAsNameNode',
    'DottedNameNode',
    'ElifNode',
    'EllipsisNode',
    'ElseAttributeNode',
    'ElseNode',
    'EndlNode',
    'ExceptNode',
    'ExecNode',
    'FinallyNode',
    'FloatExponantComplexNode',
    'FloatExponantNode',
    'FloatNode',
    'ForNode',
    'FromImportNode',
    'GeneratorComprehensionNode',
    'GetitemNode',
    'GlobalNode',
    'HexaNode',
    'IfElseBlockSiblingNode',
    'IfNode',
    'IfelseblockNode',
    'ImportNode',
    'IntNode',
    'LambdaNode',
    'LeftParenthesisNode',
    'ListArgumentNode',
    'ListComprehensionNode',
    'ListNode',
    'LongNode',
    'NameAsNameNode',
    'NameNode',
    'OctaNode',
    'PassNode',
    'PrintNode',
    'RaiseNode',
    'RawStringNode',
    'ReprNode',
    'ReturnNode',
    'RightParenthesisNode',
    'SemicolonNode',
    'SetComprehensionNode',
    'SetNode',
    'SliceNode',
    'SpaceNode',
    'StarNode',
    'StringChainNode',
    'StringNode',
    'TernaryOperatorNode',
    'TryNode',
    'TupleNode',
    'UnicodeRawStringNode',
    'UnicodeStringNode',
    'UnitaryOperatorNode',
    'WhileNode',
    'WithContextItemNode',
    'WithNode',
    'YieldAtomNode',
    'YieldNode',
])

# Those nodes create a new scope
new_scope = set([
])

# Those nodes can't contain assignments
no_assign = set([
    'ArgumentGeneratorComprehensionNode',
    'AssertNode',
])

others = [
    'AssignmentNode',
    'Node',
]

for a, b in itertools.combinations([do_enter, new_scope, no_assign, others],
                                   2):
    assert not a.insersection(b)
missing = all_nodes.difference(do_enter, new_scope, no_assign, others)
if missing:
    warnings.warn("Unhandled redbaron nodes: %s" % ', '.join(missing))


class Cell(object):
    """A piece of code that can be parsed independently.

    Dependencies are only computed between cells, no analysis happens between
    the lines of a single cell.
    """
    def __init__(self, source):
        if isinstance(source, redbaron.RedBaron):
            self.source = source
        else:
            self.source = redbaron.RedBaron(utf8(source))
        # Removes empty lines
        while self.source and isinstance(self.source[0], redbaron.EndlNode):
            del self.source[0]
        while self.source and isinstance(self.source[-1], redbaron.EndlNode):
            del self.source[-1]

        for node in self.source.find_all('AssignmentNode'):
            if node.target:

    def __unicode__(self):
        return self.source.dumps().strip()


class Flow(object):
    """A dataflow consisting of multiple cells.

    You can add, remove, and reorder cells from a Flow, and the dependencies
    will be updated automatically.
    """
    def __init__(self, cells=None):
        # Maps symbol names to the cells that use it
        self.read_by = {}
        # Maps symbols names to the cells that assign it
        self.written_by = {}

        if cells is not None:
            self._cells = list(cells)
        else:
            self._cells = [self._add(cell) for cell in cells]

    def _add(self, cell):
        if isinstance(cell, Cell):
            pass
        elif isinstance(cell, text):
            cell = Cell(cell)
        else:
            raise TypeError("Expected iterable of Cell or strings, "
                            "got %r" % type(cell))

        if cell.reads:
            for symbol in cell.reads:
                default(self.read_by, symbol, set).add(cell)

        if cell.writes:
            for symbol in cell.writes:
                default(self.written_by, symbol, set).add(cell)

        return cell

    def _rm(self, cell):
        for symbol in cell.reads:
            self.read_by[symbol].remove(cell)
        for symbol in cell.writes:
            self.written_by[symbol].remove(cell)

    def __iter__(self):
        return iter(self._cells)

    def __len__(self):
        return len(self._cells)

    def __getitem__(self, item):
        return self._cells[item]

    def __setitem__(self, key, value):
        self._rm(self._cells[key])
        self._cells[key] = self._add(value)

    def __setslice__(self, i, j, sequence):
        for cell in self._cells[i:j]:
            self._rm(cell)
        self._cells[i:j] = (self._add(cell) for cell in sequence)

    def __delitem__(self, key):
        self._rm(self._cells.pop(key))

    def __delslice__(self, i, j):
        for cell in self._cells[i:j]:
            self._rm(cell)
        del self._cells[i:j]

    def dependencies(self, cell):
        last_assign = {}
        symbols = set(cell.reads)

        for other in self._cells[self._cells.index(cell)::-1]:
            if not symbols:
                break
            for symbol in other.writes.intersection(symbols):
                last_assign[symbol] = other
            symbols.difference_update(other.writes)

        return set(itervalues(last_assign))

    def dependents(self, cell):
        last_read = {}
        symbols = set(cell.writes)

        for other in self._cells[self._cells.index(cell):]:
            if not symbols:
                break
            for symbol in other.reads.intersection(symbols):
                last_read[symbol] = other
            symbols.difference_update(other.reads)

        return set(itervalues(last_read))

    def graph(self):
        graph = {}
        last_assign = {}

        for cell in self._cells:
            deps = set()
            for symbol in cell.reads:
                try:
                    deps.add(last_assign[symbol])
                except KeyError:
                    pass
            graph[cell] = deps
            for symbol in cell.writes:
                last_assign[symbol] = cell

        return graph
