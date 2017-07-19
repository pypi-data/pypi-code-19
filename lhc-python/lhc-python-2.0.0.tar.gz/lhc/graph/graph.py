from collections import namedtuple

Edge = namedtuple('Edge', ('fr', 'to'))


class Vertex(object):
    __slots__ = ('vertex', 'children', 'parents')

    def __init__(self, vertex):
        self.children = set()
        self.parents = set()
        self.vertex = vertex

    def __iter__(self):
        yield self.vertex
        yield self.children
        yield self.parents


class Graph(object):
    """
    A graph with directed or undirected edges. Vertices must implement __hash__ and __eq__. Edges can not be labelled.
    N-partite graphs can be used to label the edges.
    """

    __slots__ = ('name', 'adjacency', 'directed')

    def __init__(self, es=list(), vs=list(), name=None, directed=True):
        """
        Initialise a graph

        :param es: list of (from, to) pairs of existing edges
        :param vs: list of vertex names (without edges)
        :param name: name of the graph
        :param directed: whether the graph is directed or not (default: True)
        """
        self.name = 'G' if name is None else name
        self.adjacency = {}  # {vertex: (vertex, children, parents)}
        self.directed = directed

        for fr, to in es:
            self.add_edge(fr, to)
        for v in vs:
            self.add_vertex(v)

    @property
    def es(self):
        for vertex, children, parents in list(self.adjacency.values()):
            for child in children:
                yield Edge(vertex, child)

    @property
    def vs(self):
        return list(self.adjacency.keys())

    def __str__(self):
        """
        Represent graph in DOT format.
        :return:
        """
        res = ['{} {} {{'.format('digraph' if self.directed else 'graph', self.name)]
        for v, children, parents in sorted(self.adjacency.values()):
            for child in children:
                res.append('    "{}" -> "{}";'.format(v, child))
        res.append('}')
        return '\n'.join(res)

    def __len__(self):
        """
        The number of vertices
        :return:
        """
        return len(self.adjacency)

    def __contains__(self, item):
        return item in self.adjacency

    def __delitem__(self, key):
        vertex, children, parents = self.adjacency.pop(key)
        for child in children:
            self.adjacency[child].parents.remove(vertex)
        for parent in parents:
            self.adjacency[parent].children.remove(vertex)

    def add_edge(self, fr, to):
        """ Add an edge to the graph. Multiple edges between the same vertices will quietly be ignored. N-partite graphs
        can be used to permit multiple edges by partitioning the graph into vertices and edges.

        :param fr: The name of the origin vertex.
        :param to: The name of the destination vertex.
        :return:
        """
        fr = self.add_vertex(fr)
        to = self.add_vertex(to)
        self.adjacency[fr].children.add(to)
        self.adjacency[to].parents.add(fr)

    def add_vertex(self, v):
        """
        Add a vertex to the graph. The vertex must implement __hash__ and __eq__ as it will be stored in a set.
        :param v: vertex
        :return: graph owned vertex
        """
        if v not in self.adjacency:
            self.adjacency[v] = Vertex(v)
        return self.adjacency[v].vertex
        
    def get_children(self, v):
        if v in self.adjacency:
            return self.adjacency[v].children
        return set()

    def get_parents(self, v):
        if v in self.adjacency:
            return self.adjacency[v].parents
        return set()

    def get_neighbours(self, v):
        if v in self.adjacency:
            return self.adjacency[v].children | self.adjacency[v].parents
        return set()

    def get_descendants(self, v):
        res = set()
        if v not in self.adjacency:
            return res
        stk = list(self.get_children(v))
        while len(stk) > 0:
            top = stk.pop()
            res.add(top)
            stk.extend(self.get_children(top) - res)
        return res

    def get_ancestors(self, v):
        res = set()
        if v not in self.adjacency:
            return res
        stk = list(self.get_parents(v))
        while len(stk) > 0:
            top = stk.pop()
            res.add(top)
            stk.extend(self.get_parents(top) - res)
        return res

    def decompose(self, removed=None):
        visited = set()
        removed = set() if removed is None else removed
        for vertex, children, parents in self.adjacency.values():
            if vertex in visited or vertex in removed:
                continue
            graph = Graph(vs=[vertex], directed=self.directed)
            stk = [vertex]
            while len(stk) > 0:
                vertex = stk.pop()
                if vertex in visited or vertex in removed:
                    continue
                visited.add(vertex)
                vertex, children, parents = self.adjacency[vertex]
                for child in children:
                    graph.add_edge(vertex, child)
                stk.extend(self.get_neighbours(vertex) - visited - removed)
            yield graph

    def update(self, other):
        for vertex in other.vs:
            self.add_vertex(vertex)
        for fr, to in other.es:
            self.add_edge(fr, to)

    def __getstate__(self):
        return tuple(getattr(self, slot) for slot in self.__slots__)

    def __setstate__(self, state):
        for slot, slot_state in zip(self.__slots__, state):
            setattr(self, slot, slot_state)
