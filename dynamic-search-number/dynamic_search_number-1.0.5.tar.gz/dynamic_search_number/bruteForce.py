import networkx as nx
import itertools

def getWidth(order):
    '''
    Given a graph G, and it's edge ordering, returns
    the linear width of that ordering.
    
    INPUT
    order: An edge ordering of G

    OUTPUT
    width: The width of order
    '''
    #We make a left and the right set of nodes incident to 1-j (left) 
    #and j + 1 - len(order) (right)

    left = set()
    right = set.union(*order)
    width = len(left.intersection(right))

    #Move the sets along by one and construct the new node lists
    for i in xrange(len(order) - 1):
        left = left.union(order[i])
        right = set.union(*(order[i + 1:]))
        #print 'For i = ', i, 'left = ', left, 'and right= ', right

        newWidth = len(left.intersection(right))

        if newWidth > width:
            width = newWidth

    return width

def linK(G, k):
    '''
    Given a graph and a positive integer k, checks whether
    the linear width of G <= k. We proceed to build an edge
    ordering by dynamic programming, and eliminate the orderings
    above k.

    INPUT
    G: A networkx graph
    k: A positive integer

    OUTPUT
    less: A boolean which is True if lin-width <= k and False otherwise.
    '''
    #We will store the orderings here as [ordering, width]
    FSi = [ [[],0] ]
    
    edges = G.edges()

    #Add edges one at a time to orderings still below k
    for edge in edges:
        newFSi = []

        for orderPair in FSi:
            order = orderPair[0][:]

            for i in xrange(0, len(order) + 1):
                #Make a new ordering by inserting the edge
                
                order = orderPair[0][:]
                order.insert(i, set(edge))

                #if the width <= k put in the new characteristic set
                newWidth = getWidth(order)
                
                if newWidth <= k:
                    newFSi.append([order, newWidth])
        
        #if newFSi is empty after adding our linear width is higher
        if len(newFSi) == 0:
            less = False
            return less

        FSi = newFSi[:]
        print 'Made a new FSi with length: ', len(FSi)

    less = True
    return less

def linearWidth(G):
    '''
    Given a graph, calculates the linear width of the graph
    by using the dynamic programming solution multiple times.

    INPUT
    G: A networkx graph

    OUTPUT
    width: The linear width of G
    '''
    #Check k until we find one where lin-width is less than k
    width = 1
    #print 'Starting a new round to check width: ', width, '\n'

    while not linK(G, width):
        width = width + 1
        #print 'Starting a new round to check width: ', width, '\n'

    return width
