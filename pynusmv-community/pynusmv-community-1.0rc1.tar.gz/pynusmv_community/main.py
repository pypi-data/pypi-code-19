'''
This is the main module that is used to kickstart the problem generation and
analysis.
'''
import pandas

from pynusmv.init      import init_nusmv
from pynusmv.glob      import load
from pynusmv.bmc.glob  import BmcSupport

from pynusmv_community import cmdline
from pynusmv_community import core
from pynusmv_community import dump
from pynusmv_community import visualization
from pynusmv_community import mining


IDLE = cmdline.do_nothing_flags()

@cmdline.log_verbose
def analyze_one(model, bound, formula=None, flags = IDLE):
    '''
    Analyzes the `model` for one given depth and one given `formula`. This step
    generates one dataframe of statistics corresponding to a shallow analysis
    of the problem. However, the analysis can be enriched with the following
    flags to produce additional artifacts (side effects) to help make a deeper
    analysis.
    
        + 'dimacs = True' will produce a *.cnf file containing the dimacs
           representation of the problem
        + 'structure = True' will produce a *.png file visually representing the 
           variable graph.
        + 'clouds = True' will produce a wordcloud (*.png file) per analyzed
           community to show the semantic information that occurs the most often
           in that community.
           
    .. note::
        It is assumed that pynusmv is initialized, the model is loaded and 
        the bmc sub system is ready to operate too.
        
    :param model: the name of the model being treated. This serves no point 
        besides 'self documentation' (generating the folder structures with 
        the appropriate names)
    :param bound: the number of time steps to generate on the problem path
    :param formula: an LTL formula to be checked via model checking (may be None)
    
    :return: a dictionary collecting the informations about the instance, its 
        bound and the number of communities and the graph modularity. This can
        be later collected into a dataframe to build evolution statistics
    '''
    cnf      = core.mk_cnf(bound, formula)
    graph    = core.mk_graph(cnf)
    clusters = graph.community_multilevel()
    
    # generate the dumps
    if flags.dump_cnf:
        dump.dimacs(model, bound, cnf)
        
    if flags.dump_mapping:
        dump.mapping(model, bound, cnf)
        
    if flags.dump_communities:
        dump.communities_curated(model, bound, clusters, graph)
        
    if flags.dump_raw_communities:
        dump.communities_raw(model, bound, clusters, graph)
        
    if flags.dump_semantic_communities:
        dump.communities_semantic(model, bound, clusters, graph)
        
    if flags.dump_json_cluster_graph:
        dump.json_cluster_graph(model, bound, clusters, graph)

    
    # generate the visualization artifacts
    if flags.show_vig:
        visualization.vig(model, bound, clusters, graph)
        
    if flags.show_cluster_graph:
        visualization.cluster_graph(model, bound, clusters, graph)
    
    if flags.show_d3_cluster_graph: 
        visualization.d3_visualisation(model, bound, clusters, graph)
        
    if flags.show_clouds:
        visualization.clouds(model, bound, clusters, graph)
    
    if flags.show_time_table:
        visualization.table_visualisation(model, bound, clusters, graph)
    
    if flags.show_formal_concepts:
        mining.mine_concept(model, bound, clusters, graph)
    
    # mine frequent_patterns
    if flags.mine_patterns:
        mining.dump_frequent_patterns(model, bound, clusters, graph)
    
    # mine frequent sequences    
    if flags.mine_sequences:
        mining.dump_frequent_sequences(model, bound, clusters, graph)
    
    return  {
            'instance'     : [model], 
            'bound'        : [bound],
            '#communities' : [core.community_count(clusters)],
            'modularity'   : [clusters.modularity]
            }
    

def analyze_all(model, formula = None, depths = range(10), flags = IDLE):
    '''
    Repeatedly performs the analysis of `model` for all `depth`. By default,
    this analysis generates no output. However the following flags can be 
    customized to generate derived artifacts.
    
        + 'dimacs = True' will produce a *.cnf file containing the dimacs
           representation of the problem
        + 'structure = True' will produce a *.png file visually representing the 
           variable graph.
        + 'clouds = True' will produce a wordcloud (*.png file) per analyzed
           community to show the semantic information that occurs the most often
           in that community.
        + 'stats  = True' will produce a csv file containing all the raw 
           statistical data alongside with two charts plotting the evolution of
           the #communities and modulatity over time
    
    .. note::
        It is assumed that pynusmv is initialized, the model is loaded and 
        the bmc sub system is ready to operate too.
    
    :param model: the name of the model being treated. This serves no point 
        besides 'self documentation' (generating the folder structures with 
        the appropriate names)
    :param formula: an LTL formula to be checked via model checking (may be None)
    :param depths: a range of path lengths for which to generate and analyze
        SAT problems.
    '''
    frames = []
    for bound in depths:
        record = analyze_one(model, bound, formula, flags)
        frames.append( pandas.DataFrame.from_dict(record) )
    
    if frames:
        data = pandas.concat(frames)
        
        if flags.dump_stats:
            dump.statistics(model, data)
        
        if flags.show_stats:
            visualization.statistics(model, data)
        

def process(path_to, model, formula = None, depths = range(10), flags = IDLE):
    '''
    Initializes PyNuSMV and loads the model, then proceeds to the bulk of the
    analysis. See `analyze_one` and `analyze_all` for further details about 
    what is done.
    
    By default, this analysis generates no output. However the following flags 
    can be customized to generate derived artifacts.
    
        + 'dimacs = True' will produce a *.cnf file containing the dimacs
           representation of the problem
        + 'structure = True' will produce a *.png file visually representing the 
           variable graph.
        + 'clouds = True' will produce a wordcloud (*.png file) per analyzed
           community to show the semantic information that occurs the most often
           in that community.
        + 'stats  = True' will produce a csv file containing all the raw 
           statistical data alongside with two charts plotting the evolution of
           the #communities and modulatity over time
    '''
    
    with init_nusmv():
        load(core.merge_model_text(path_to, model+".smv"))
        
        with BmcSupport():
            analyze_all(model, formula, depths, flags)
            
def main():
    '''
    The main entry point of the tool. See --help for the full details of what
    it can do.
    '''
    args = cmdline.parse_args()
    rng  = range(args.min_bound, 1+args.max_bound)
    process(args.path, args.model, args.formula, rng, args)
    
if __name__ == "__main__":
    main()