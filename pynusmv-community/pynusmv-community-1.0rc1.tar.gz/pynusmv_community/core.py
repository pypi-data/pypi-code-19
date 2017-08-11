'''
This module contains some utility function that help analyze BMC instances
'''
import math
import concepts

# # PyNuSMV
# import pynusmv.init          as _init
# import pynusmv.glob          as _glob
# import pynusmv.node          as _node
# import pynusmv.parser        as _parser
# 
# # BMC related stuffs
# import pynusmv.bmc.glob      as _bmc
# import pynusmv.bmc.utils     as _utils
# import pynusmv.bmc.ltlspec   as _ltlspec
# import pynusmv.be.fsm        as _fsm
# import pynusmv.be.manager    as _mgr
# import pynusmv.be.encoder    as _enc
# import pynusmv.be.expression as _exp

############### SHOULD MOVE TO PYNUSMV (core) #################################

def cnf_to_be_var(literal):
    import pynusmv.be.encoder as _enc
    '''
    .. important::
        Converts a cnf literal (int, aka dimacs representation) into a `BeVar`
        object representing the same bit but having much more semantic info
        (ie, its name and time)
        
    .. note::
        If no concrete value exists for some literal (as in the case of aux var
        that have no model correspondant), this function returns None
        
    .. remark::
        This functionality should move and be merged into the core of pynusmv
    
    :param literal: the literal (int, aka dimacs repr) of the literal
    :return: a `BeVar` object representing the given literal but provinding 
        plenty of additional meta-data about that bit.  
    '''
    enc    = _enc.BeEnc.global_singleton_instance()
    mgr    = enc.manager
    # This line can fail because of the 0 return value
    #idx   = mgr.cnf_literal_to_index(literal)
    be_lit = mgr.cnf_literal_to_be_literal(literal)
    idx    = mgr.be_literal_to_index(be_lit)         if be_lit != 0 else 0
    var    = _enc.BeVar(enc, idx)                    if idx    != 0 else None
    return var

def short_var_repr(var):
    '''
    .. remark::
        This functionality should move and be merged into the core of pynusmv
    
    :param var: the `BeVar` whose short description is desired
    :return: a short string representation of the given variable
    '''
    import re
    
    # Skip the case where no var is given
    if not var:
        return '???'
    
    # recognizes a string that starts with an identifier and ends with a .digit
    expr = re.compile('^(?P<name>[\w\.]+)\.(?P<bit>\d+)$')
    found= expr.match( str(var.name) )
    
    if found:
        name = found.group('name')
        bit  = found.group('bit')
        return "{}*bit_{}*at_{}".format(name, bit, var.time)
    else:
        return "{}*at_{}".format(var.name, var.time)


############### CONVERSIONS IGRAPH <--> PYNUSMV ###############################

def vertex_to_lit(graph, vertex):
    '''
    :param vertex: an integer denoting the igraph identifier of some vertex
    :return: the CNF literal associated with some `vertex`
    '''
    return graph.vs[vertex]['lit']

def vertex_to_be_var(graph, vertex):
    '''
    :param graph: a graph having the 'lit' attribute set for all vertices 
        and containing `vertex` 
    :param vertex: a boolean variable of the problem as it is represented in the
        associated graph.
    :return: The `BeVar` associated with the literal represented by `vertex` in
        the `graph`
    '''
    return cnf_to_be_var(vertex_to_lit(graph, vertex))
 
def vertex_repr(graph, vertex):
    '''
    :param graph: a graph having the 'lit' attribute set for all vertices 
        and containing `vertex` 
    :param vertex: a boolean variable of the problem as it is represented in the
        associated graph.
    :return: a  short string representation of the semantic info associated with
        the `vertex` in the `graph`
    '''
    return short_var_repr(vertex_to_be_var(graph, vertex))

def semantic_vars(graph):
    '''
    Lists all the semantic variables that intervene in the problem.
    '''
    result = set()
    for vertex in graph.vs:
        literal= vertex['lit']
        be_var = cnf_to_be_var(literal)
        repres = short_var_repr(be_var)
        name   = repres.split(sep="*")[0]
        result.add(name)
        
    return sorted( list( result ) )

############### GENERATION UTILS #############################################

def mk_cnf_no_formula(bound):
    '''
    :return: a `BeCnf` expression representing the model + `bound` steps of 
    unrolled transition relation
    '''
    import pynusmv.bmc.utils as _utils
    
    model = _utils.BmcModel()
    cnf   = model.path(bound).to_cnf()
    return cnf

def mk_cnf_with_formula(formula, bound):
    '''
    :return: a `BeCnf` expression representing the verification of `formula` on
    the loaded model for a `bound` time steps    
    '''
    import pynusmv.node        as _node
    import pynusmv.parser      as _parser
    import pynusmv.bmc.glob    as _bmc
    import pynusmv.bmc.ltlspec as _ltlspec
    
    prop    = _node.Node.from_ptr( _parser.parse_ltl_spec(formula) )
    fsm     = _bmc.master_be_fsm()
    problem = _ltlspec.generate_ltl_problem(fsm, prop, bound).to_cnf()
    return problem

def mk_cnf(bound, formula=None):
    '''
    :return: a sat instance for the current problem regardless of whether there
    is an associated formula
    '''
    return mk_cnf_with_formula(formula, bound) if formula else mk_cnf_no_formula(bound)

def mk_graph(cnf):
    '''
    Generates a variable relationship graph.
    
    In this graph there is one vertex per VARIABLE (thus we do not 
    distinguish between the two possible literals for a var) and there is
    one edge between two variables iff their literals belong to one same 
    clause. 
    
    .. note::
        The dimacs CNF format declares way more variables than are actually
        used. This is a waste of resources and it makes the output cluttered
        and hardly analyzable.
    '''
    import igraph
    
    counter  = 0
    canonical= {} 
    
    edgelist = []
    lit_attr = []
    # still \Theta(n^2) but already better.
    for clause in cnf.clauses_list:
        for i in range(len(clause)):
            for j in range(i+1, len(clause)):
                # no distinction between literals for one variable
                source = abs(clause[i])
                dest   = abs(clause[j])
                
                if source not in canonical:
                    canonical[source] = counter
                    lit_attr.append(source)
                    counter += 1
                
                if dest not in canonical:
                    canonical[dest] = counter
                    lit_attr.append(dest)
                    counter += 1
                
                c_src = canonical[source]
                c_dst = canonical[dest]
                edgelist.append((c_src, c_dst))
    
    return igraph.Graph(n=counter, edges=edgelist, vertex_attrs={'lit': lit_attr})

############### MISC UTILITIES ################################################

def merge_model_text(path_to, model):
    '''
    An utility method that permits the loading of multi-files models using 
    includes macros. This is required in order to deal with models that would
    otherwise require the `-cpp` flag to be passed on to NuSMV.
    (This is necessary because the M4 preprocessor is not available in pynusmv)
    
    :param path_to: the path to the folder containing the 'main' model that has
        to be loaded.
    :param model: the main model that has to be loaded
    :return: a complete version of the model with all the inclusions inlined
    '''
    import re
    import os.path
    inclusion = re.compile('#include\s+"(?P<included>.+)"')
    
    with open(os.path.join(path_to, model), 'r') as f:
        acc = []
        for line in f:
            found = inclusion.match(line)
            if found:
                included = found.group("included")
                acc.append(merge_model_text( path_to,  included) )
            else:
                acc.append(line.rstrip())
        
        # add a final trailing blank line
        acc.append(" ")
        return '\n'.join(acc)
    
def to_dimacs(cnf):
    '''
    An alternative to `pynusmv.bmc.ltlspec:dump_dimacs_filename` which generates
    less verbose dimacs files and permits to have them all loaded in memory.
    
    :param cnf: a `BeCnf` expression to encode in dimacs format
    :return: a string representation of the `cnf` formula in DIMACS CNF format
    '''
    heading   = 'p cnf {} {}'.format(cnf.vars_number, cnf.clauses_number)
    d_clauses = [ heading ]
    
    for clause in cnf.clauses_list:
        text_form = ' '.join( map(str, clause) ) + ' 0'
        d_clauses.append( text_form )
    
    return '\n'.join(d_clauses) 

def community_count(clustering):
    '''
    Counts the number of community in a fairer way than simply using 
    len(clustering). Indeed, the former method counts single nodes as a 
    community while this is not considered desirable. Hence, this method
    counts the number of communities having 2+ nodes.
    '''
    nb_communities = 0
    for cluster in clustering:
        if len(cluster) >= 2:
            nb_communities += 1
    return nb_communities

def graph_to_json(graph):
    '''
    Generates a JSON representation of the given graph
    '''
    # format strings
    v_format = '{{ "id": {}, "community": {}, "size" : {} , "normal" : {}  }}'
    e_format = '{{ "src":{}, "dst": {}, "weight": {}, "thickness" : {} }}'
    g_format = '{{ "nodes" : [ {} ], "edges" : [ {} ] }}'
    
    # Vertex specific transformations
    v_min    = min(graph.vs['size'])
    v_attr   = lambda v,a: graph.vs[a][v.index]
    v_comu   = lambda v: v_attr(v, 'community')
    v_size   = lambda v: v_attr(v, 'size')
    v_normal = lambda v: math.sqrt( v_size(v) / v_min )
    v_json   = lambda v: v_format.format(v_comu(v)-1, v_comu(v), v_size(v), v_normal(v))
    
    # Edge specific transformations
    e_attr   = lambda e,a: graph.es[a][e.index]
    e_weight = lambda e: e_attr(e, "weight")
    e_json   = lambda e: e_format.format(e.source, e.target, e_weight(e), math.log(e_weight(e)) )
    
    vs_json  = ',\n'.join([ v_json(v) for v in graph.vs ])
    es_json  = ',\n'.join([ e_json(e) for e in graph.es ])
    g_json   = g_format.format(vs_json, es_json)
    
    return g_json
    
def graph_to_fca_context(graph, tokenize=True):
    '''
    Uses the given `graph` to generate an FCA context. 
    This feature is useful when you want to apply formal concept analysis
    to detect the possible semantic meaning of the the community structure of
    a bounded model checking problem instance.
    
    :param graph: the graph to use to produce the FCA context
    :param tokenize: split the semantic names into token (increases the chances
        of fca finding something interesting)
    '''
    d = concepts.Definition()
    
    for vertex in range(len(graph.vs)):
        repres = vertex_repr(graph, vertex)
        
        var_info   = repres.split(sep="*")
        var_name   = var_info[0]
        var_block  = var_info[-1]
        
        if tokenize:
            var_tokens = var_name.split(sep=".")
            d.add_object(str(vertex), var_tokens + [var_block] )
        else:
            d.add_object(str(vertex), [var_name, var_block] )
    
    return concepts.Context(*d)