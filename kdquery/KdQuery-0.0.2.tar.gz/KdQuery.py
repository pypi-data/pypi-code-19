# -*- coding: utf-8 -*-

"""Kd-tree implementation.

This module contains one possible kd-tree structure implementation and a
general method capable to find the nearest node from a query for any kd-tree
structure.

"""
import math

from collections import deque


def interval_condition(value, inf, sup, dist):
    """Checks if value belongs to the interval [inf - dist, sup + dist].
    """
    return (value > inf - dist and value < sup + dist)


def spherical_dist(point1, point2):
    theta = point1[0] - point2[0]
    phi = point1[1] - point2[1]
    return math.acos(math.cos(theta) * math.cos(phi))


def euclidean_dist(point1, point2):
    return math.sqrt(sum([math.pow(point1[i] - point2[i], 2)
                          for i in range(len(point1))]))


class Node:
    """Internal represantation of a node.

    The tree is represented by a list of node. Each node is associated to a
    point in the k-dimensional space, is inside a region, devides this region
    in two parts according to an axis, has two child nodes and stores some
    data.

    Attributes:
        point (:obj:`tuple` of float or int): Stores the position of the node.
        region (:obj:`list` of :obj:`list` of float or int): A list of size
            k, where each list contais two numbers defining the limits of the
            region in which the node is.
        active (bool): True by default. If it`s False, this node can`t be the
            output of a nearest_point query.
        axis (int): Represents one particular dimension of the space.
            Relatively to this dimension, all the nodes to the left are smaller
            and all the nodes to the right are greater.
        left (int): Identifier of the left child in the internal represenation
            of a kd-tree.
        right (int): Identifier of the right child in the internal
            represenation of a kd-tree.
        data (:obj): The information stored by the node.

    Example:
        >>> point = (0, 4.2, 3)
        >>> region = [[-3, 1], [4, 4.5], [2, 7 ]]
        >>> data = dict('name': 'my_node', label': green, 'weight': 893.3)
        >>> node = Node(point, region, 1, data)

    """

    def __init__(self, point, region, axis, data):
        self.point = point
        self.region = region
        self.axis = axis
        self.active = True
        self.left = None
        self.right = None
        self.data = data

    def desactivate(self):
        self.active = False

    def get_properties(self):
        return (self.point, self.region, self.axis, self.active,
                self.left, self.right)


class Tree:
    """Kd-tree implementation.

    This class defines one implemention of a kd-tree using a python list to
    save the methods from recursion.

    Attributes:
        node_list (:obj:`list` of :obj:Node): The list of nodes.
        size (int): The number of active nodes in the list.
        next_identifier (int): The identifier of the next node to be inserted
            in the list.
        k (int): The number of dimensions of the space.
        capacity (int): The maximum number of nodes in the tree.

    """

    def __init__(self, k, capacity):
        self.node_list = [None] * capacity
        self.size = 0
        self.next_identifier = 0
        self.k = k

    def __len__(self):
        return self.size

    def __iter__(self):
        return (self.get_node(node_id) for node_id in range(self.size))

    def get_node(self, node_id):
        return self.node_list[node_id]

    def disactivate(self, node_id):
        """Disactivate the node identified by node_id.

        Disactivates the node corresponding to node_id, which means that
        it can never be the output of a nearest_point query.

        Note:
            The node is not removed from the tree, its data is steel avaiable.

        Args:
            node_id (int): The node indentifier (given to the user after
                its insertion).

        """
        self.get_node(node_id).desactivate()
        self.size -= 1

    def insert(self, point, data=None):
        """Insert a new node in the tree.

        Args:
            point (:obj:`tuple` of float or int): Stores the position of the
                node.
            data (:obj): The information stored by the node.

        Returns:
            int: The identifier of the new node.

        Example:
            >>> tree = Tree(4, 800)
            >>> point = (3, 7)
            >>> data = dict('name': Fresnel, 'label': blue, 'speed': 98.2)
            >>>
            >>> node_id = tree.insert(point, data)

        """
        assert len(point) == self.k

        if self.size == 0:
            region = [[-math.inf, math.inf]] * self.k
            axis = 0
            return self.new_node(point, region, axis, data)

        # Iteratively descends to one leaf
        parent_node = self.node_list[0]
        while True:
            axis = parent_node.axis
            if point[axis % self.k] < parent_node.point[axis % self.k]:
                child = parent_node.left
                left = True
            else:
                child = parent_node.right
                left = False

            if child is None:
                break

            parent_node = self.node_list[child]

        # Get the region delimited by the parent node
        region = parent_node.region[:]
        region[axis] = parent_node.region[axis][:]

        # Limit to the child`s region
        new_limit = parent_node.point[axis]

        # Update reference to the new node
        if left:
            parent_node.left = self.size
            region[axis][1] = new_limit
        else:
            parent_node.right = self.size
            region[axis][0] = new_limit

        return self.new_node(point, region, (axis + 1) % self.k, data)

    def new_node(self, point, region, axis, data):
        node = Node(point, region, axis, data)

        # Identifier to new node
        node_id = self.next_identifier
        self.node_list[node_id] = node

        self.size += 1
        self.next_identifier += 1

        return node_id

    def find_nearest_point(self, query, dist_fun=euclidean_dist):
        """Find the point in the tree that minimizes the distance to the query.

        Args:
            query (:obj:`tuple` of float or int): Stores the position of the
                node.
            dist_fun (:obj:`function`): The distance function.

        Returns:
            :obj:`tuple`: Tuple of length 3, where the first element is the
                identifier of the nearest node, the second is the distance
                to the query and the third is the number of distance operations
                that were computed during the search.

        Example:
            >>> tree = Tree(2, 3)
            >>> tree.insert((0, 0)); tree.insert((3, 5)); tree.insert((-1, 7));
            >>>
            >>> query = (-1, 8)
            >>> nearest_node_id, dist, count = tree.find_nearest_point(query)
            >>> dist
            1

        """
        def get_properties(node_id):
            return self.get_node(node_id).get_properties()

        return Tree.nearest_point(query, 0, get_properties, dist_fun)

    @staticmethod
    def nearest_point(query, root_id, get_properties, dist_fun=euclidean_dist):
        """Find the point in the tree that minimizes the distance to the query.

        This method implements the nearest_point query for any structure
        implementing a kd-tree. The only requirement is a function capable to
        extract the relevant properties from a node represantation of the
        particular implemetation.

        Args:
            query (:obj:`tuple` of float or int): Stores the position of the
                node.
            root_id (:obj): The identifier of the root in the kd-tree
                implementation.
            get_properties (:obj:`function`): The function to extract the
                relevant properties from a node, namely its point, region,
                axis, left child identifier, right child identifier and
                if it is active. If the implemetation does not uses
                the active attribute the function should return always True.
            dist_fun (:obj:`function`): The distance function.

        Returns:
            :obj:`tuple`: Tuple of length 3, where the first element is the
                identifier of the nearest node, the second is the distance
                to the query and the third is the number of distance operations
                that were computed during the search.

        """

        k = len(query)
        dist = math.inf

        nearest_node_id = None

        # stack_node: stack of identifiers to nodes within a region that
        # contains the query.
        # stack_look: stack of identifiers to nodes within a region that
        # does not contains the query.
        stack_node = deque([root_id])
        stack_look = deque()

        count = 0
        while stack_node or stack_look:

            if stack_node:
                node_id = stack_node.pop()
                look_node = False
            else:
                node_id = stack_look.pop()
                look_node = True

            point, region, axis, active, left, right = get_properties(node_id)

            # Should consider this node?
            # As it is within a region that does not contains the query, maybe
            # there is no chance to find a closer node in this region
            if look_node:
                inside_region = True
                for i in range(k):
                    inside_region &= interval_condition(query[i], region[i][0],
                                                        region[i][1], dist)
                if not inside_region:
                    continue

            # Update the distance only if the node is active.
            if active:
                node_distance = dist_fun(query, point)
                if nearest_node_id is None or dist > node_distance:
                    nearest_node_id = node_id
                    dist = node_distance

            if query[axis] < point[axis]:
                side_node = left
                side_look = right
            else:
                side_node = right
                side_look = left

            if side_node is not None:
                stack_node.append(side_node)

            if side_look is not None:
                stack_look.append(side_look)

            count += 1

        return nearest_node_id, dist, count
