"""
    Utility functions for processing tsp problems.
    Points are represented by the datastructure Node, which consists
    of an id and the x and y coordinates."""
from random import randint, sample
import os
import math
import re
import ast



def parse_tsp_file(file):
    """ Parses data from a tspfile with regexes and returns a tuple
    holding the nodes and groupinformation"""
    # define regular expressions for the fields to parse
    regexes = {'name': re.compile("NAME : (.*)"),
               'comment': re.compile("COMMENT : (?!STARTNODE :|STARTNODES : |CLUSTERS :)(.*)"),
               'single_start': re.compile("COMMENT : STARTNODE : ([0-9])+"),
               'multi_start': re.compile("COMMENT : STARTNODES : (.*)"),
               'nodes':
               re.compile(
                   r"([0-9]+)\ *([0-9]*\.?[0-9]*)\ *([0-9]*\.?[0-9]*)",
                   re.MULTILINE),
               'groups': re.compile("COMMENT : CLUSTERS : (.*)")}
    # initialize results
    result = {'name': 'No Name', 'comment': '', 'startnodes': [],
              'nodes': [], 'groups': []}
    # Define application rules

    def apply_match(regex_name, match):
        """Applies a specific processing rule for each regex sperately as the
        fields vary in data types and structures"""
        if regex_name is 'name':
            result['name'] = match.group(1)
        elif regex_name is 'single_start':
            result['startnodes'] = [int(match.group(1))]
        elif regex_name is 'multi_start':
            result['startnodes'] = ast.literal_eval(match.group(1))
        elif regex_name is 'groups':
            result['groups'] = ast.literal_eval(
                match.group(1).replace(" ", ""))
        elif regex_name is 'comment':
            result['comment'] += match.group(1) + "\n"
        elif regex_name is 'nodes':
            result['nodes'].append([int(float(match.group(2))),
                                    int(float(match.group(3)))])
    # Process the lines in the file and check for matches for each regular
    # expression
    _file = open(file, 'r')
    lines = _file.readlines()
    for line in lines:
        if len(line):
            for regex_name in regexes:
                match = re.match(regexes[regex_name], line)
                if match:
                    apply_match(regex_name, match)
    _file.close()
    return result


def parse_solutions(solutionsfile):
    """Parses a file containing solutions. The solutions must be given in separate rows and
    can not include other characters than spaces and numbers. The numbers must be separated by
    single spaces. The returned solutions are all zero indexed."""
    result = []
    with open(solutionsfile) as fp:
        for line in fp:
          result.append(zero_index_path(line.strip().split(" ")))
    return result

def dist(start, end, scale=1):
    """ Calculates the euclidean distance between the two nodes start and end.
        start: Node
        end: Node """
    return math.sqrt(math.pow((start.x_coord * scale - end.x_coord * scale), 2) +
                     math.pow((start.y_coord * scale - end.y_coord * scale), 2))


def path_length(nodes, path, scale=1):
    """ Calculates the length of the given path.
        nodes: Array of nodes,
        scale: a scalar to multiply the coordinates with
        path: Array of indices """
    result = 0
    for point in range(0, len(path) - 1):
        start = nodes[int(path[point])]
        end = nodes[int(path[point + 1])]
        result += dist(start, end, scale)
    return result


def nearest_neighbor(nodes, origin, scale=1):
    """ Finds the distance of the nearest neighbor. Returns a tuple
    of the index of the neighbor node in the nodes array and the
    corresponding distance."""
    distances = [dist(origin, node, scale) for node in nodes]
    if origin in nodes:
        distances[nodes.index(origin)] = float("Inf")
    result = min(distances)
    return (distances.index(result), result)


def generate_problem(dimension, bounds):
    """ Generates a problem of $dimension points within
        the specified coordinate bounds"""
    while True:
        # generate a list of random points
        points = [(randint(bounds[0], bounds[1]) * 100,
                   randint(bounds[2], bounds[3]) * 100) for x in range(dimension)]
        # if there are no duplicates, exit the loop. otherwise generate a new list
        points = list(set(points))
        if len(points) == dimension:
            break
    # construct nodes with the points
    nodes = [Node(i, p[0], p[1]) for i, p in enumerate(points)]
    return nodes

def reindex_nodes(nodes):
    """ Assigns node ids to a list of nodes according to their
        position in the list"""
    for (index, node) in enumerate(nodes):
        node.node_id = index

def on_segment(p, q, r):
    """Returns True if the point q (x,y) lies on the line between p and r. """
    return (q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0]) and
            q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1]))

def orientation(p, q, r):
    """ Returns 1 if p q r are oriented clockwise, 2 if p q r are oriented
        counterclockwise and 0 if p q r lie on a line - are collinear."""
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    if (val == 0):
        return 0
    if (val > 0):
        return 1
    else:
        return 2

def do_intersect(p1, q1, p2, q2):
    """ Returns True if the line p and q intersect"""
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)
    if not (o1 == o2 or o3 == o4):
        return True
    if (o1 == 0 and on_segment(p1, p2, q1)):
        return True;
    if (o2 == 0 and on_segment(p1, q2, q1)):
        return True;
    if (o3 == 0 and on_segment(p2, p1, q2)):
        return True;
    if (o4 == 0 and on_segment(p2, q1, q2)):
        return True;

def has_path_intersections(nodes, path):
    """ Returns True, if the path has intersections."""
    path = zero_index_path(path)
    for i in range(0, len(path) - 4):
        p1 = nodes[path[i]]
        q1 = nodes[path[i + 1]]
        for j in range (i + 2, len(path) - 1):
            p2 = nodes[path[j]]
            q2 = nodes[path[j + 1]]
            if(do_intersect(p1,q1,p2,q2)):
                if not p1 == q2:
                    return True
    return False

def coords2nodes(points):
    result = [Node(i,p[0],p[1]) for i,p in enumerate(points)]
    if len(result) == 1:
        return result[0]
    else:
        return result

def nodes2coords(nodes):
    return [(n.x_coord, n.y_coord) for n in nodes]

def find_node_by_coords(coords, nodes):
    """returns the first node, that has the given coordinates"""
    (x_value, y_value) = coords
    node = [node for node in nodes if ((node.x_coord == x_value) and
                                       (node.y_coord == y_value))]
    if len(node):
        return node[0]
    else:
        return None


def convex_hull_angles(nodes):
    """Returns the angles on the corner points of the convex hull for the given
    problem. Interior nodes are assigned an infinite angle."""
    # get the convex hull
    K = convex_hull_helper(nodes)
    #Drop the last element - it is the startpoint
    K.pop()
    #get the nodes on the hull
    n = len(K)
    thetas = [float("inf") for x in range(len(nodes))]
    for i in range(0, n):
        j = (i+1) % n # % n handles the index overflow at the last node
        k = i-1
        #get the vectors to the two neighbor nodes
        v1 = (K[i] - K[j])
        v2 = (K[i] - K[k])
        #calculate the dotproduct between the vectors
        d = sum(p*q for p,q in zip(list(v1.get_coords()), list(v2.get_coords())))
        #calculate the lengths of the vectors
        origin = Node(-1,0,0)
        n1 = dist(origin, v1)
        n2 = dist(origin, v2)
        #calculate the angle between the vectors
        thetas[K[i].node_id] = math.degrees(math.acos(d/(n1*n2)))
    return thetas

def convex_hull_helper(nodes):
    """ calls the convex hull function and constructs the path
        with the corresponding node objects"""
    if len(nodes):
        # convert nodes into points (x,y)
        points = [(node.x_coord, node.y_coord) for node in nodes]
        # get convex hull as list of ids
        result = [find_node_by_coords(point, nodes) for
                  point in convex_hull(points)]
        result.append(result[0])
        return result
    else:
        return None


def convex_hull(points):
    """Computes the convex hull of a set of 2D points.

    Input: an iterable sequence of (x, y) pairs representing the points.
    Output: a list of vertices of the convex hull in counter-clockwise order,
      starting from the vertex with the lexicographically smallest coordinates.
    Implements Andrew's monotone chain algorithm. O(n log n) complexity.

    SRC: http://en.wikibooks.org/wiki/Algorithm_Implementation/Geometry/Convex_hull/Monotone_chain#Python

    NOTE:
    Can be changed to include nodes directly lying on an edge of the
    convex hull. See 'CHANGE' comments in code.
    """

    # Sort the points lexicographically (tuples are compared lexicographically)
    # Remove duplicates to detect the case we have just one unique point.

    points = sorted(set(points))

    # Boring case: no points or a single point, possibly repeated multiple
    # times.
    if len(points) <= 1:
        return points

    def cross(point_o, point_a, point_b):
        """ 2D cross product of OA and OB vectors, i.e. z-component of their
        3D cross product.
        Returns a positive value, if OAB makes a counter-clockwise turn,
        negative for clockwise turn, and zero if the points are collinear."""
        return ((point_a[0] - point_o[0]) * (point_b[1] - point_o[1]) -
                (point_a[1] - point_o[1]) * (point_b[0] - point_o[0]))

    # Build lower hull
    lower = []
    for point in points:
        # CHANGE:
        # To include nodes on the edges:
        # while len(lower) >= 2 and cross(lower[-2], lower[-1], p) < 0:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)

    # Build upper hull
    upper = []
    for point in reversed(points):
        # CHANGE:
        # To include nodes on the edges:
        # while len(upper) >= 2 and cross(upper[-2], upper[-1], p) < 0:
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)

    # Concatenation of the lower and upper hulls gives the convex hull.
    # Last point of each list is omitted because it is repeated at the
    # beginning of the other list.
    return lower[:-1] + upper[:-1]

def export_tsp(nodes, scale, comment, filename):
    """ Exports the problem data in .tsp format  """
    if comment is None:
        comment = "PUT PROBLEM DESCRIPTION HERE"
    # check if the function was called with a filename
    # check if the user did select a file
    if filename:
        _file = open(filename, 'w')
        _file.write("NAME : " + os.path.basename(filename) + "\n")
        _file.write("COMMENT : " + comment + "\n")

        groups = construct_groups_string(nodes)
        if not groups == "":
            _file.write("COMMENT : CLUSTERS : " + groups + "\n")

        startnodes = construct_startnodes_string(nodes)
        if not startnodes == "":
            _file.write("COMMENT : STARTNODES : " + startnodes + "\n")

        _file.write("TYPE: TSP" + "\n")
        _file.write("DIMENSION: " + str(len(nodes)) + "\n")
        _file.write("EDGE_WEIGHT_TYPE : EUC_2D" + "\n")
        _file.write("NODE_COORD_SECTION" + "\n")

        for (index, node) in enumerate(nodes):
            _file.write(str(index + 1) + "  " + str(node.x_coord * scale) +
                        " " + str(node.y_coord * scale) + "\n")
        _file.write("EOF")
        _file.close()
        return os.path.basename(filename)


def export_tikz(nodes, scale, path, filename):
    """ Exports the problem data as a tikz graphic in .tex format  """
    if filename:
        _file = open(filename, 'w')

        _file.write("\\begin{tikzpicture}\n")
        _file.write("\\begin{axis}[%\n")
        _file.write("width=\\textwidth,\n")
        _file.write("scale only axis,\n")
        _file.write("xmin=-100,\n")
        _file.write("xmax=2700,\n")
        _file.write("ymin=-100,\n")
        _file.write("ymax=2100,\n")
        _file.write("y dir=reverse,\n")
        _file.write("axis x line*=bottom,\n")
        _file.write("axis y line*=left\n")
        _file.write("]\n")

        for group in get_groups(nodes):
            _file.write(
                """\\addplot [color=black,mark size=5.0pt,
                        only marks,mark=*,mark options={solid,
                        fill=""" + group.lower() + "},forget plot]\n")
            _file.write("table[row sep=crcr]{%\n")
            for node in nodes:
                if node.color == group:
                    _file.write(
                        str(node.x_coord * scale) + " " +
                        str(node.y_coord * scale) + "\\\\\n")
            _file.write("};\n")

        if not path is None:
            _file.write("\\addplot [draw=black,forget plot]\n")
            _file.write("table[row sep=crcr]{%\n")
            for path_node in path['Tour']:
                node = nodes[int(path_node)]
                _file.write(
                        str(node.x_coord * scale) + " " +
                        str(node.y_coord * scale) + "\\\\\n")
            _file.write("};\n")
        _file.write("\\end{axis}\n")
        _file.write("\\end{tikzpicture}%\n")
        _file.close()


def get_groups(nodes):
    """ return an array holding all occuring colorids of the given nodeset"""
    return list(set([node.color for node in nodes]))


def construct_groups_string(nodes):
    """ Constructs a string representing the grouping of nodes """
    groups = get_groups(nodes)
    if len(groups) <= 1:
        return ""
    else:
        result = []
        for color in groups:
            # +1 because .tsp nodes are indexed with 1
            group = [node.node_id + 1 for node in nodes if node.color == color]
            result.append(group)
        return str(result)


def construct_startnodes_string(nodes):
    """ Looksup every node with the start bit and constructs a string of
        the list of the ids of those nodes."""
    res = [node.node_id for node in nodes if node.start]
    if len(res):
        return str(res)
    else:
        return ""

def cycle_path_to_zero(path):
    """ Cycles the path to be started with the node with index 0."""
    return cycle_path_to_index(path, 0)

def cycle_path_to_index(path, index):
    if path[0] == path[-1]:
        path = path[:-1]
    while int(path[0]) != index:
        path = path[1:] + path[:1]
    path.append(path[0])
    return path

def zero_index_path(tour):
    """ Shifts down the indices in a path, so the lowest number is zero."""
    tourint = [int(n) for n in tour]
    minidx = min(tourint)
    if minidx == 0:
        return tourint
    else:
        fixed = [n - minidx for n in tourint]
        return fixed

def randomsamples(solutions, samples):
    """ Returns an array of random samples from the input array. The number of samples
    can be an arbitrary number or the keyword 'All'."""
    if samples == "All":
        samples = len(solutions)
    data = sample(solutions, samples)
    return data



def connection_matrix(solutions, normalize=False):
    """ Takes a list of solutions and constructs a matrix counting the connections
    between nodes for all solutions. If normalize is True all values are divided by
    the number of total connections. The summation of matrix entries then yields 1.0."""
    dimension = len(solutions[0])
    #initialize
    rows = [[0 for x in range(0,dimension)] for y in range (0,dimension)]
    for sol in solutions:
        for i in range(0,len(sol)-1):
            rows[int(sol[i])][int(sol[i+1])] = rows[int(sol[i])][int(sol[i+1])] + 1
    if normalize:
        #normalize counts
        for i,row in enumerate(rows):
            rows[i] = [float(x)/(float(len(solutions)) * dimension) for x in row]
    return rows



def connection_matrix_layerwise(solutions, normalize=False):
    """Same as connection_matrix, but will construct a connection matrix for each step in
    the solutions. For example are 4 steps needed to produce the solution [0 1 2 3 0]"""
    dimension = len(solutions[0])-1
    #initialize
    layers = [[[0 for x in range(0,dimension)] for y in range (0,dimension)] for l in range(0,dimension)]
    for sol in solutions:
        for i in range(0,len(sol)-1):
            layers[i][sol[i]][sol[i+1]] += 1

    if normalize:
        #normalize counts
        for layer in layers:
            for i,row in enumerate(layer):
                rows[i] = [float(x)/(float(len(solutions))) for x in row]
    return layers




def startnode_frequencies(solutions):
    """Takes a list of solutions and counts the number of occurances of each possible node
    as a starting point / at position 0 in the solution set."""
    result = [0 for x in range(0,len(solutions[0]))]
    for path in solutions:
        result[path[0]] = result[path[0]] + 1
    return result

def distinct_solutions(sols):
    """ Take a list of solutions and returns the a dictionary of distinct (different) solutions.
    The solutions are key, the number of occurrences of the solution in the original set is value.
    The returned solutions are all indexed and shifted to zero.
    Two solutions are considered equal if the order of point indices is the same, even if the start
    is different. The reversed version of a solution is also considered equal."""
    solutions = {}
    result = {}
    for line in sols:
        path = zero_index_path(line)
        path = cycle_path_to_zero(path)
        if str(path) in solutions:
            solutions[str(path)] += 1
        elif str(path[::-1]) in solutions:
            solutions[str(path[::-1])] += 1
        else:
            solutions[str(path)] = 1
    return solutions





class Node(object):
    def __init__(self, node_id, x, y, color='BLACK', start=False):
        self.node_id = node_id
        self.x_coord = x
        self.y_coord = y
        self.color = color
        self.start = False

    def __str__(self):
        """ Construct a string with the node information """
        xdelim = ""
        ydelim = ""
        if self.x_coord < 10:
            xdelim = "  "
        if self.y_coord < 10:
            ydelim = "  "

        result = (str(self.node_id) + "     X:" + xdelim + str(self.x_coord)
                  + "      Y:" + ydelim + str(self.y_coord))
        if self.start:
            result += "     Start"
        return result

    def __sub__(self, other):
        return Node(-1, self.x_coord - other.x_coord,
                        self.y_coord - other.y_coord)

    def get_coords(self):
        """ returns the node coordinates as a tuple"""
        return (self.x_coord, self.y_coord)
