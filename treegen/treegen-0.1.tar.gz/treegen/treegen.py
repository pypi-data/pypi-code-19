'''
A small tool for enumeration of non-isomorphic rooted trees.

Implements the Wright, Richmond, Odlyzko, and McKay (WROM) algorithm.

Author: Steven Schmatz (@stevenschmatz)
Contact: stevenschmatz@gmail.com
'''

from typing import List, Generator, Tuple


VertexIndex = int
LevelOrderTree = List[VertexIndex]


def split_tree(layout: LevelOrderTree) -> Tuple[LevelOrderTree, LevelOrderTree]:
    '''
    Search for the second child of root, and separate the child
    subtree from the parent subtree.
    '''

    ones = [index for index, val in enumerate(layout) if val == 1]
    split_index = ones[1] if len(ones) > 1 else len(layout)

    left_subtree = [node - 1 for node in layout[1:split_index]]
    remaining_subtree = [0] + layout[split_index:]

    return left_subtree, remaining_subtree


def generate_centered_tree_layout(n_vertices: int) -> LevelOrderTree:
    '''
    A centered tree is a set of vertices whose maximum distance from
    other vertices is minimized.
    '''

    tree_one = range(n_vertices // 2 + 1)
    tree_two = range(1, (n_vertices + 1) // 2)

    return list(tree_one) + list(tree_two)


def next_rooted_tree(predecessor: LevelOrderTree, left_order: int = None):
    '''Finds the nearest adjacent rooted non-isomorphic tree.'''

    if left_order is None:
        left_order = len(predecessor) - 1
        while predecessor[left_order] == 1:
            left_order -= 1

    # Stop condition
    if left_order == 0:
        return None

    q = left_order - 1
    while predecessor[q] != predecessor[left_order] - 1:
        q -= 1

    result = list(predecessor)
    for i in range(left_order, len(result)):
        result[i] = result[i - left_order + q]

    return result

def candidate_valid(l_tree: LevelOrderTree, r_tree: LevelOrderTree) -> Tuple[bool, int]:
    '''
    Determines if a candidate tree split will lead to a non-isomorphic tree.

    Returns:
    - valid
    - order of the left subtree (only required for invalid trees)
    '''

    l_height, r_height = max(l_tree), max(r_tree)

    if l_height > r_height:
        return False, len(l_tree)

    l_order, r_order = len(l_tree), len(r_tree)

    if l_height == r_height:
        if l_order > r_order:
            return False, l_order
        elif l_order == r_order and l_tree > r_tree:
            return False, l_order

    return True, l_order


def generate_new_candidate(candidate: LevelOrderTree, left_subtree_order: int) -> LevelOrderTree:
    '''
    Generates a valid candidate tree by splitting the tree and extending
    the other side with a suffix.
    '''

    new_candidate = next_rooted_tree(candidate, left_subtree_order)

    if candidate[left_subtree_order] > 2:
        new_left_subtree, new_remaining_subtree = split_tree(new_candidate)
        new_left_height = max(new_left_subtree)
        suffix = range(1, new_left_height + 2)
        new_candidate[-len(suffix):] = suffix

    return new_candidate


def next_tree(candidate: LevelOrderTree) -> LevelOrderTree:
    '''Returns the next valid tree layout for a given tree.'''

    left_subtree, remaining_subtree = split_tree(candidate)
    valid, l_order = candidate_valid(left_subtree, remaining_subtree)

    if valid:
        return candidate
    else:
        return generate_new_candidate(candidate, l_order)


def generate_trees_level_order(n_vertices: int) -> Generator[LevelOrderTree, None, None]:
    '''
    Generates all rooted, non-isomorphic trees with the number of vertices specified.
    Returns a flat list of integers representing a level-order traversal.
    '''

    if n_vertices <= 0:
        raise ValueError('Number of vertices provided was less than one.')

    elif n_vertices == 1:
        return []

    layout = generate_centered_tree_layout(n_vertices)

    while layout is not None:
        layout = next_tree(layout)
        if layout != None:
            yield layout
            layout = next_rooted_tree(layout)


def level_order_to_adjacency_matrix(tree: LevelOrderTree) -> List[List[int]]:
    '''Converts the adjacency matrix for the given level order traversal.'''

    matrix = [[0] * len(tree) for i in range(len(tree))]

    stack = []
    for index, level in enumerate(tree):
        if len(stack) > 0:
            stack_top = stack[-1]
            top_level = tree[stack_top]

            while top_level >= level:
                stack.pop()
                stack_top = stack[-1]
                top_level = tree[stack_top]

            matrix[index][stack_top] = matrix[stack_top][index] = 1
        stack.append(index)

    return matrix


def generate_trees_adjacency_matrix(n_vertices: int) -> List[List]:
    '''
    Generates all rooted, non-isomorphic trees with the number of vertices specified.
    Returns an adjacency matrix of the graph.
    '''

    for level_order_tree in generate_trees_level_order(n_vertices):
        yield level_order_to_adjacency_matrix(level_order_tree)

def non_isomorphic_rooted_tree_count(n_vertices: int) -> int:
    oeis_counts = [1, 1, 1, 1, 2, 3, 6, 11, 23, 47, 106, 235, 551, 1301, 3159, 7741, 19320, 48629, 123867, 317955, 823065, 2144505, 5623756, 14828074, 39299897, 104636890, 279793450, 751065460, 2023443032, 5469566585, 14830871802, 40330829030, 109972410221, 300628862480, 823779631721, 2262366343746, 6226306037178]

    if n_vertices < len(oeis_counts):
        return oeis_counts[n_vertices]
    else:
        raise ValueError(f'Number of vertices must be less than {len(oeis_counts)}')
