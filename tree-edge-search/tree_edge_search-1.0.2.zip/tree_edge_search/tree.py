'''
The O(nlog(n)) time algorithm for calculating the search number of a tree
given in [1].

[1]: The Complexity of Searching a Graph. N. Megiddo et. al.
'''
import networkx as nx

def isEdge(graph):
    '''
    Given a graph, checks whether it is just an edge.

    INPUT
    graph: A NetworkX graph

    OUTPUT
    edge: Boolean on whether the graph is an edge
    '''
    edge = False

    #An edge has two nodes with only one edge between them
    nodes = graph.nodes()
    edges = graph.edges()

    if len(nodes) == 2 and len(edges) == 1:
        if graph.has_edge(nodes[0], nodes[1]):
            edge = True
            return edge

    return edge

def reRoot(tree, origRoot):
    '''
    Given an input of a tree and a first root, 
    changes the root to one of it's neighbours and
    continues info computation.

    INPUT
    tree: A networkx tree graph
    origRoot: The root that was selected first. Has degree = 1

    OUTPUT
    treeInfo: info calculated with the new root and adjusted
    according to pg.8 of [1]
    '''
    #Find the neighbour of origRoot
    neighbors = tree.neighbors(origRoot)

    if len(neighbors) == 0:
        #We have a graph with one node
        return ['E', 1, None]
    
    root = neighbors[0]

    #Calculate the new treeInfo with the root
    treeInfo = info(tree, root)

    #Adjust the the treeInfo
    if treeInfo[0] == 'H':
        treeInfo[0] = 'E'
    elif treeInfo[0] == 'I' and treeInfo[1] == 1:
        treeInfo[0] = 'E'
    elif treeInfo[0] == 'I' and treeInfo[1] != 1:
        treeInfo[0] = 'M'
        treeInfo[2] = ['E', 1, None]

    #TODO: We are not properly considering the M-info of the last case
    return treeInfo

def split(tree, root):  
    '''
    Given a tree and a root, creates two trees.

    INPUT
    tree: A networkx tree graph
    root: A root node of degree at least two

    OUTPUT
    trees [tree1, tree2]: Two trees disjoint except for root whose
    union makes tree.
    '''
    #Get the neighborhood of root
    neighbors = tree.neighbors(root)
    
    #Choose the first neighbor to remove
    removeNode = neighbors[0]
    
    #Make the tree with the vertex removed
    removedTree1 = tree.copy()
    removedTree1.remove_node(removeNode)
    tree1 = nx.ego_graph(removedTree1, root, radius = float('inf'))

    #Make the tree with everything but the selected vertex removed
    removedTree2 = tree.copy()

    for i in range(1, len(neighbors)):
        removedTree2.remove_node(neighbors[i])

    tree2 = nx.ego_graph(removedTree2, root, radius = float('inf'))

    return [tree1, tree2]

def merge(info1, info2):
    '''
    Given info for two trees, merges their info records
    as per page 9 of [1].

    INPUT
    info1: The info record for tree1 in a split
    info2: The info record for tree2 in a split

    OUTPUT
    mergedInfo: The merged info records
    '''
    #Extract the search numbers, types and M-info
    type1 = info1[0]
    type2 = info2[0]
    s1 = info1[1]
    s2 = info2[1]
    Minfo1 = info1[2]
    Minfo2 = info2[2]

    #Check if the search numbers are equal and test cases 1-5
    if s1 == s2:
        if type1 == 'H' and type2 == 'H':
            mergedInfo = ['H', s1, None]
        elif (type1 == 'H' and type2 == 'E') or \
        (type1 == 'E' and type2 == 'H'):
            mergedInfo = ['E', s1, None]
        elif type1 == 'E' and type2 == 'E':
            mergedInfo = ['I', s1, None]
        elif (type1 == 'I' and type2 == 'H') or \
        (type1 == 'H' and type2 == 'I'):
            mergedInfo = ['I', s1, None]
        elif type1 == 'M' or type2 == 'M':
            mergedInfo = ['H', s1 + 1, None]
        elif type1 == 'I' and type2 == 'I':
            mergedInfo = ['H', s1 + 1, None]
        elif (type1 == 'I' and type2 == 'E') or \
        (type1 == 'E' and type2 == 'I'):
            mergedInfo = ['H', s1 + 1, None]
    elif s1 > s2:
        #Do cases 6-7 for s1>s2
        
        if type1 == 'H' or type1 == 'E' or type1 == 'I':
            mergedInfo = [type1, s1, None]
        elif type1 == 'M':
            
            #Merge the two info records
            MinfoMerge = merge(Minfo1, info2)
            sPrime = MinfoMerge[1]

            if sPrime < s1:
                mergedInfo = ['M', s1, MinfoMerge]
            elif sPrime == s1:
                mergedInfo = ['H', s1 + 1, None]
    elif s2 > s1:
        #Do cases 6-7 for s2>s1
        
        if type2 == 'H' or type2 == 'E' or type2 == 'I':
            mergedInfo = [type2, s2, None]
        elif type2 == 'M':
            
            #Merge the two info records
            MinfoMerge = merge(Minfo2, info1)
            sPrime = MinfoMerge[1]

            if sPrime < s2:
                mergedInfo = ['M', s2, MinfoMerge]
            elif sPrime == s2:
                mergedInfo = ['H', s2 + 1, None]

    return mergedInfo

def info(tree, root):
    '''
    Given an input of a tree graph, calculates the root's info 
    as in [1]. This function is recursive.

    INPUT
    tree: A networkx tree graph
    root: A vertex from tree that is the current root of tree

    OUTPUT
    treeInfo: The info for the current tree.
    '''
    
    #Calculate the degree of the root
    degree = nx.degree(tree, root)
    
    #Use reroot if the deg is 1 and merges otherwise
    if degree == 0:
        treeInfo = ['H', 1, None]    
    elif degree == 1:

        #A single edge has search number = 1
        if isEdge(tree):
            treeInfo = ['E', 1, None]
        else: 
            #Since tree is not an edge, we re-root and keep going
            treeInfo = reRoot(tree, root)
    else:
        
        #Split the tree into two trees rooted at root
        trees = split(tree, root)
        
        #Calculate the info for each tree and merge
        info1 = info(trees[0], root)
        info2 = info(trees[1], root)
        treeInfo = merge(info1, info2)

    return treeInfo
        

def computeInfo(tree):
    '''
    Given an input of a tree computes
    [type, s(T), M-info(T)]

    INPUT
    tree: A networkx tree graph

    OUTPUT
    info [type, s(T), M-info(T)]: See page 8 of [1].
    '''

    #Make the root the first node
    root = tree.nodes()[0]
    
    #Get the info for tree
    information = info(tree, root)

    return information

def edge_search(tree):
    '''
    Returns the search number of an inputed tree.

    INPUT
    tree: A networkx tree graph

    OUTPUT
    searchNumber: The search number of tree
    '''
    
    information = computeInfo(tree)
    searchNumber = information[1]

    return searchNumber
