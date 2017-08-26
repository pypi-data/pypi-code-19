#-*- coding: utf-8 -*-

import json
from abc import ABC


class NotTreeTypeException(Exception):
    """Raises when the object is not a tree instance."""


# ###########################################################################


class Tree(ABC):

    """
    An n-ary tree where each node has refrence to parent and childrens.
    """

    def __init__(self, parent = None, children = None, **data):

        from collections import OrderedDict
        
        # Is it necessary to use ordered dictionary?
        self._data = OrderedDict((k, data[k]) for k in sorted(data) \
                if k not in ('parent', 'children'))

        self._parent = parent

        # Should we write some validation method?
        if parent is not None:
            if not isinstance(parent, Tree):
                raise NotTreeTypeException
            parent.add_child(self)
            
        if children is None:
            self._children = []
        else:
            self._children = [c for c in children if isinstance(c, Tree)]

    @property
    def data(self):
        return self._data

    @property
    def parent(self):
        """
        Returns the parent node if any or `None`.

        Examples:
            
            >>> tree = Tree(number = 1)
            >>> tree.parent        
            None

            >>> tree = Tree(None, number = 1)
            >>> tree.parent
            None

        """  
        return self._parent

    @parent.setter
    def parent(self, value):
        
        if value is self:
            raise ValueError('Loops are not allowed.')
        
        # + cannot be subtree

        self._parent = value

        if self.parent is not None:
            self.parent.add_child(self) # can raise 

    @property
    def children(self):
        return tuple(self._children)

    @property 
    def depth(self):
        return NotImplemented

    def add_child(self, child):
        """
        Adds the child node.
        """
        
        if not isinstance(child, type(self)):
            raise NotTreeTypeException('Child must be tree.')
        
        self._children.append(child)

    def remove_child(self, child):
        """
        Removes the child node.
        """
        # TODO Use setter for children?
        self._children = [c for c in self.children if c is not child]
    
        child.parent = None

    @property
    def is_root(self):
        return self.parent is None

    @property
    def is_leaf(self):
        return len(self.children) == 0

    @property
    def is_perfect(self):
        return NotImplemented

    @property
    def is_complete(self):
        return NotImplemented

    @property
    def has_any_parent(self):
        return self.parent is not None

    def has_parent(self, parent):
        return self.parent is parent

    @property
    def has_any_child(self):
        return len(self.children) > 0
    
    def has_child(self, child):
        return child in self.children

    @property
    def ancestors(self):
        """
        Return the parents of this node and his parent and so on.
        """
        return NotImplemented

    def __eq__(self, other):
        if self is other:
            return True
        return self.data == other.data \
            and all([s == o for s, o in zip(self.children, other.children)])

    def __hash__(self):
        return hash((self.data, self.parent, self.children))

    def __str__(self):
        parent_id = id(self.parent) if self.parent is not None else None
        return "Tree(data={}, parent={}, children=[{}])".\
            format(self.data, parent_id, ';'.join([str(id(c)) for c in self.children]))

    def __repr__(self):
        return str(self)
   
    def to_dict(self):

        return {
            'data': self.data,
            'children': {
                'count': len(self.children),
                'nodes': [child.to_dict() for child in self.children]
            }
        }

    def to_json(self):
        return json.dumps(self.to_dict())


'''FIXME
class BinaryTree(Tree):

    def __init__(self, data, parent = None, left_child = None, right_child = None):
        super().__init__(parent, (left_child, right_child), data)
      
    @property
    def left_child(self):
        return self.children[0]

    @property
    def right_child(self):
        return self.children[1]

# ###########################################################################

def binary_tree(parent = None, left_child = None, right_child = None, *args, **kwargs):
    """Creates the binary tree with given parent, left and right child and data. 
    """

    data = [v for v in kwargs.values() if v not in ('parent', 'left_child', 'right_child')]  + [i for i in args]
    
    binary_tree = BinaryTreeNode(tuple(data)    , parent, left_child, right_child)
    
    return binary_tree
'''

# ###########################################################################
# Factory functions
# ###########################################################################


def make_root():
    pass


def make_child(parent, data):
    pass


def make_parent(child, data):
    pass


def render_to_console(tree):
    """TODO"""
    print("├── ", tree)
    for tree in tree.children:
        render_to_console(tree)


# ###########################################################################


if __name__ == '__main__':

    # DEMO
    
    class Token: 

        def __init__(self, lemma):
            self.lemma = lemma

        def __str__(self):
            return "Token(lemma={})".format(self.lemma)


    class SentenceTree(Tree):

        def __init__(self, parent, children, token):
            super().__init__(parent, children, token = token)

        @Tree.data.getter
        def data(self):
            return super().data['token']
    

    node0 = SentenceTree(None, None, Token('lemma1'))   
    node1 = SentenceTree(node0, None, token=Token('lemma2'))
    node2 = SentenceTree(node0, None, token=Token('lemma3'))
    
    print(node2, "leaf={}, root={}".format(node2.is_leaf, node2.is_root))
    print(node1, "leaf={}, root={}".format(node1.is_leaf, node1.is_root))
    print(node0, "leaf={}, root={}".format(node0.is_leaf, node0.is_root))

    render_to_console(node0)