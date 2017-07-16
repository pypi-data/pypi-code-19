# Copyright 2016 Suzy M. Stiegelmeyer
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
'''
intevalTree.py is an adaptation of the interval tree algorithm based on
red-black trees from Introduction to Algorithms by Cormen, Leiserson, Rivest
and Stein (2001) 2nd Edition, The MIT Press

This makes a nice self-balancing tree.  The alrogithm may be more efficient
if items are randomly selected for insertion, instead of in sort order.

I've modified the CLRS algorithm to report all overlapping nodes instead of
only the first node.  This involved adding a min value instead of only a max
value in order to speed up the search by checking if the subtree min,max
overlaps with the search interval.  The search routine is also recursive.
'''
#
# 2010-05-31 S. Stiegelmeyer Created
# 2014-08-21 S. stiegelmeyer Added closestNode method to find closest interval
#                            to non-overlapping interval
# 2014-09-29 S. Stiegelmeyer Fixed bugs in closestNode method and removed
#                            rightChild method
# 2017-07-15 S. Stiegelmeyer Add more document strings
import sys

RED = 0
BLACK = 1


def overlap(x1, y1, x2, y2):
    """ Calculates if two intervals overlap with one another.
        Input:
            x1 - min value of interval 1
            y1 - max value of interval 1
            x2 - min value of interval 2
            y2 - max value of interval 2
        Output:
            Boolean indicating overlap (True) or no overlap (False)
    """
    lap = False
    if x1 <= y2 and x2 <= y1:
        lap = True
    return lap


def traverseInOrder(node):
    """ In Order traversal of tree.  Should see list from smallest to largest
        by x value.
        Input:
            node - node to begin traversal
        Output:
            intervals are printed out.
    """
    if node.eiTree is not None:
        traverseInOrder(node.eiTree)
    if node.left is not None:
        traverseInOrder(node.left)
    sys.stdout.write(node)
    if node.right is not None:
        traverseInOrder(node.right)


def searchTSS(node, pt):
    """Routine for closest transcription start site (TSS).
    Don't use. Not finished.
    """
    found = False
    while not found:
        if node.left is not None and node.right is not None:
            l = abs(node.left.tss-pt)
            r = abs(node.right.tss-pt)
            p = abs(node.tss-pt)
            minlist = [l, r, p]
            minval = min(l, r, p)
            index = minlist.index(minval)
            if index == 0:
                node = node.left
            elif index == 1:
                node = node.right
            else:
                found = True
        elif node.left is not None:
            l = abs(node.left.tss-pt)
            p = abs(node.tss-pt)
            minval = min(l, p)
            if l < p:
                node = node.left
            else:
                found = True
        elif node.right is not None:
            r = abs(node.right.tss-pt)
            p = abs(node.tss-pt)
            minval = min(r, p)
            if r < p:
                node = node.right
            else:
                found = True
        else:
            minval = abs(node.tss-pt)
            found = True
    return (node.name, minval)


def deleteTree(node):
    '''
    Given a root node, recursively delete the interval tree.
    Input:
        node - initially the root node
    Output:
        none
    '''
    if node.eiTree is not None:
        deleteTree(node.eiTree)
    if node.left is not None:
        deleteTree(node.left)
    if node.right is not None:
        deleteTree(node.right)

    del(node)


def searchTree(node, mi, ma):
    """ Find all nodes which overlap with the input interval.
        Input:
            node - node to begin traversal, usually the root
            mi - minimum value of interval
            ma - maximum value of interval
        Output:
            list of nodes which overlap with input interval.
    """
    ret = []

    if node.left is not None and overlap(mi, ma, node.left.min, node.left.max):
        ret.extend(searchTree(node.left, mi, ma))
    if overlap(mi, ma, node.x, node.y):
        ret.append(node)
    if node.right is not None and \
       overlap(mi, ma, node.right.min, node.right.max):
        ret.extend(searchTree(node.right, mi, ma))
    return ret


def closestNode(node, mi, ma):
    """ Find the node that is closest to the input interval
        Input:
          node - node to begin traversal, usually the root
          mi - minimum value of interval
          ma - maximum value of interval
        Output:
          closest node, None if nodes overlap
    """
    ret = None
    while node is not None:
        if overlap(mi, ma, node.x, node.y):
            node = None
            prev = None
        elif node.left is not None and \
                overlap(mi, ma, node.left.min, node.left.max):
            prev = node
            node = node.left
        elif node.right is not None and \
                overlap(mi, ma, node.right.min, node.right.max):
            prev = node
            node = node.right
        else:
            prev = node
            node = None
    if prev is not None:
        if prev.x > ma:
            # get max node in left tree
            if prev.left is not None:
                if ma < prev.left.min:
                    node = prev.left.minimumNode()
                else:
                    node = prev.left.maximumNode()
                a = prev.x - ma
                b = mi - node.y
                if a < b:
                    ret = prev
                else:
                    ret = node
            else:
                ret = prev
        else:  # get min node in right tree
            if prev.right is not None:
                if mi > prev.right.max:
                    node = prev.right.maximumNode()
                else:
                    node = prev.right.minimumNode()
                a = mi-prev.y
                b = node.x-ma
                if a < b:
                    ret = prev
                else:
                    ret = node
            else:
                ret = prev
    return ret


def searchGeneName(node, name):
    """ Find node or nodes which match input gene name.
        Input:
            node - node to begin traversal, usually the root
            name - name to match with node.name
        Output:
            list of all nodes which match name
    """
    ret = []
    if node.name == name:
        ret.append(node)
    if node.left is not None:
        ret.extend(searchGeneName(node.left, name))
    if node.right is not None:
        ret.extend(searchGeneName(node.right, name))
    return ret


class Tree:
    def __init__(self,
                 mi=0,
                 ma=0,
                 tss=0,
                 tes=0,
                 strand="-",
                 name="",
                 name2="",
                 cdsS=0,
                 cdsE=0,
                 eTree=None,
                 eType=0,
                 misc=[]):
        self.x = mi
        self.y = ma
        self.max = ma
        self.min = mi
        self.strand = strand
        self.name = name
        self.name2 = name2
        self.tss = tss
        self.tes = tes
        self.cdsStart = cdsS
        self.cdsEnd = cdsE
        self.exontype = eType
        self.eiTree = eTree
        self.color = RED
        self.left = None
        self.right = None
        self.p = None
        self.misc = misc

    def __repr__(self):
        return "({0.x!r},{0.y!r}),({0.cdsStart!r},{0.cdsEnd!r}),\
            {0.exontype!r}".format(self)

    def __str__(self):
        return "({0.x!r}, {0.y!r}, {0.max!r}) {0.color!r} {0.name!r} \
            {0.strand!r} {0.exontype!r}".format(self)

    def insertTree(self, root):
        """ Insert node in tree given the root node
            Input:
                root - root of tree
            Output:
                root
        """
        nodesave = None
        node = root
        while node is not None:
            nodesave = node
            if self.x < node.x or (self.x == node.x and self.y >= node.y):
                node = node.left
            else:
                node = node.right
        self.p = nodesave
        if nodesave is None:
            root = self
        elif self.x < nodesave.x or \
                (self.x == nodesave.x and self.y >= nodesave.y):
            nodesave.left = self
        else:
            nodesave.right = self
        self.left = None
        self.right = None
        self.color = RED
        self.updateMax()
        self.updateMin()
        root = self.insertFixup(root)
        return root

    def insertFixup(self, root):
        """ Routine to ensure the tree is balanced
            Input:
                root - root of tree
            Output:
                root
        """
        z = self
        while z is not None and z.p is not None and z.p.color == RED:
            if z.p.p is not None and z.p == z.p.p.left:
                y = z.p.p.right
                if y is not None and y.color == RED:
                    z.p.color = BLACK
                    y.color = BLACK
                    z.p.p.color = RED
                    z = z.p.p
                else:
                    if z == z.p.right:
                        z = z.p
                        root = z.leftRotate(root)
                    z.p.color = BLACK
                    z.p.p.color = RED
                    root = z.p.p.rightRotate(root)
            elif z.p.p is not None and z.p == z.p.p.right:
                y = z.p.p.left
                # sentinal pointer is always black
                if y is not None and y.color == RED:
                    z.p.color = BLACK
                    y.color = BLACK
                    z.p.p.color = RED
                    z = z.p.p
                else:
                    if z == z.p.left:
                        z = z.p
                        root = z.rightRotate(root)
                    z.p.color = BLACK
                    z.p.p.color = RED
                    root = z.p.p.leftRotate(root)
        root.color = BLACK
        return root

    def maximum(self):
        """ Calculate the maximum of (self.y, self.left.max, self.right.max)
        """
        t1 = self.y
        t2 = self.left.max if self.left is not None else 0
        t3 = self.right.max if self.right is not None else 0
        if t2 > t1:
            t1 = t2
        if t3 > t1:
            t1 = t3
        self.max = t1

    def minimum(self):
        """ Calculate the minimum of (self.x, self.left.min, self.right.min)
        """
        t1 = self.x
        t2 = self.left.min if self.left is not None else self.x
        t3 = self.right.min if self.right is not None else self.x
        if t2 < t1:
            t1 = t2
        if t3 < t1:
            t1 = t3
        self.min = t1

    def updateMax(self):
        """ Updates the max value for all parent nodes
        """
        tmp = self
        while tmp is not None:
            tmp.maximum()
            tmp = tmp.p

    def updateMin(self):
        """ Updates the min value for all parent nodes
        """
        tmp = self
        while tmp is not None:
            tmp.minimum()
            tmp = tmp.p

    def leftRotate(self, root):
        """ Routine to help maintain tree balance by performing a left rotation
            Input:
                root - root of tree
            Output:
                root
        """
        node = self.right  # x = self; y=x.right
        self.right = node.left  # x.right=y.left
        if node.left is not None:
            node.left.p = self  # parent pointers  y.left.p=x
        node.p = self.p   # y.p = x.p
        if self.p is None:
            root = node     # root = y
        elif self == self.p.left:  # x == x.p.left
            self.p.left = node     # x.p.left = y
        else:
            self.p.right = node    # x.p.right = y
        node.left = self           # y.left = x
        self.p = node              # x.p = y
#        self.updateMax()
#        self.updateMin()
        self.maximum()
        self.minimum()
        node.maximum()
        node.minimum()
        return root

    def rightRotate(self, root):
        """ Routine to help maintain tree balance by performing a right rotation
            Input:
                root - root of tree
            Output:
                root
        """
        node = self.left
        self.left = node.right
        if node.right is not None:
            node.right.p = self
        node.p = self.p
        if self.p is None:
            root = node
        elif self.p.left == self:
            self.p.left = node
        else:
            self.p.right = node
        node.right = self
        self.p = node
#        self.updateMax()
#        self.updateMin()
        self.maximum()
        self.minimum()
        node.maximum()
        node.minimum()
        return root

    def maximumNode(self):
        '''
        Find the node with the maximum value
        Input:
            self - tree node
        Output:
            maximum node
        '''
        x = self
        while x.right is not None:
            x = x.right
        return x

    def minimumNode(self):
        '''
        Find the node with the minimum value
        Input:
            self - tree node
        Output:
            minimum node
        '''
        x = self
        while x.left is not None:
            x = x.left
        return x

    def successorNode(self):
        '''Find the successor node'''
        x = self
        if x.right is not None:
            return x.right.minimumNode()
        y = x.p
        while y is not None and x == y.right:
            x = y
            y = y.p
        return y

    def deleteNode(self, root):
        """ Delete node from tree given the root node
        ***This does not work***
            Input:
                self: node to delete
                root: root of tree
            Output:
                root
        """
        z = self
        if z.left is None or z.right is None:
            y = z
        else:
            y = z.successorNode()
        if y.left is not None:
            x = y.left
        else:
            x = y.right
        if x is not None:
            x.p = y.p
        if y.p == z:
            u = y
        else:
            u = y.p
        if y.p is None:
            root = x
        else:
            if y == y.p.left:
                y.p.left = x
                y.p.minimum()
                y.p.maximum()
            else:
                y.p.right = x
                y.p.minimum()
                y.p.maximum()
        savcolor = y.color
        if y != z:
            if z.p is None:
                root = y
            if z.p is not None and z.p.left == z:
                z.p.left = y
            elif z.p is not None and z.p.right == z:
                z.p.right = y
            y.p = z.p
            y.color = z.color
            y.left = z.left
            if y.left is not None:
                y.left.p = y
            y.right = z.right
            if y.right is not None:
                y.right.p = y
            y.minimum()
            y.maximum()
        if savcolor == BLACK:
            if x is not None:
                root = x.deleteFixup(root, False)
            # if u is none then there are no nodes in the tree
            elif u is not None:
                # x's "parent" is y's old parent
                root = u.deleteFixup(root, True)

        del(z)
        if u is not None:
            u.updateMax()
            u.updateMin()
        return root

    def deleteFixup(self, root, sentinel):
        '''Routine to ensure the tree is balanced after removing a node'''
        if sentinel:
            x = None
            parent = self
        else:
            x = self
            parent = x.p
        while x != root and (x is None or x.color == BLACK):
            if x == parent.left:
                w = parent.right
                if w is not None and w.color == RED:
                    w.color = BLACK
                    parent.color = RED
                    root = parent.leftRotate(root)
                    w = parent.right
                if (w is not None) and \
                        (w.left is None or w.left.color == BLACK) and \
                        (w.right is None or w.right.color == BLACK):
                    w.color = RED
                    x = parent
                    parent = x.p
                else:
                    if (w is not None) and \
                            (w.right is None or w.right.color == BLACK):
                        if w.left is not None:
                            w.left.color = BLACK
                        w.color = RED
                        root = w.rightRotate(root)
                        w = parent.right
                    if w is not None:
                        w.color = parent.color
                    parent.color = BLACK
                    if w is not None:
                        w.right.color = BLACK
                    root = parent.leftRotate(root)
                    x = root
            elif x == parent.right:
                w = parent.left
                if w is not None and w.color == RED:
                    w.color = BLACK
                    parent.color = RED
                    root = parent.rightRotate(root)
                    w = parent.left
                if (w is not None) and \
                        (w.left is None or w.left.color == BLACK) and \
                        (w.right is None or w.right.color == BLACK):
                    w.color = RED
                    x = parent
                    parent = x.p
                else:
                    if (w is not None) and \
                            (w.left is None or w.left.color == BLACK):
                        if w.right is not None:
                            w.right.color = BLACK
                        w.color = RED
                        root = w.leftRotate(root)
                        w = parent.left
                    if w is not None:
                        w.color = parent.color
                    parent.color = BLACK
                    if w is not None:
                        w.left.color = BLACK
                    root = parent.rightRotate(root)
                    x = root

        if x is not None:
            x.color = BLACK
        return root

    def prevNode(self):
        '''Previous node in tree'''
        node = None
        if self.left is not None:
            node = self.left.maximumNode()
        if self.left is None and self.p is not None and self.p.right == self:
            node = self.p
        elif self.left is None and self.p is not None and self.p.left == self:
            node = self.p
            while node is not None and node.x > self.x:
                node = node.p
        return node

    def nextNode(self):
        '''Next node in tree'''
        node = None
        if self.right is not None:
            node = self.right.minimumNode()
        if self.right is None and self.p is not None and self.p.left == self:
            node = self.p
        elif self.right is None and \
                self.p is not None and self.p.right == self:
            node = self.p
            while node is not None and node.y < self.y:
                node = node.p
        return node
