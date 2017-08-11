'''
This module contains nothing but the logic to parse the command line arguments
'''
import argparse

from collections import namedtuple 

# Is the verbosity turned on ?
__VERBOSE = False

def arguments():
    args = argparse.ArgumentParser(description="""
        A tool to analyze the community structure of SAT BMC problem instances
    """)
    
    verbose           = args.add_argument("-v", "--verbose", action="store_true")
    verbose.help      = 'Verbose information during the run'

    ################## PROBLEM CONFIG #########################################
    general           = args.add_argument_group('Problem')
    general.help      = 'Configuration of the problem to analyze'
    
    model             = general.add_argument("model")
    model.help        = "The model to load"
    
    path_to           = general.add_argument("--path")
    path_to.help      = "The path to the folder containing the 'main' module"
    path_to.default   = '.'
    
    min_bound         = general.add_argument("-k", "--min-bound", type=int)
    min_bound.help    = "The minimal problem size"
    min_bound.default = 0
    
    max_bound         = general.add_argument("-K", "--max-bound", type=int)
    max_bound.help    = "The maximal problem size"
    max_bound.default = 10
    
    formula           = general.add_argument("-f", "--formula")
    formula.help      = "A formula to generate the model checking problem"
    
    ################## DUMP COMMAND ###########################################
    dump              = args.add_argument_group("Dump")
    dump.help         = "Generate some raw data files about the analyzed instance(s)"
    
    dimacs            = dump.add_argument("--dump-cnf", action="store_true")
    dimacs.help       = 'Generate a DIMACS .cnf file for each instance' 
    
    mapping           = dump.add_argument("--dump-mapping", action="store_true")
    mapping.help      = 'Text file containing a mapping cnf var -> SMV meaning'
    
    commu             = dump.add_argument("--dump-communities", action="store_true")
    commu.help        = 'Text file containing the curated communities clustering'
    
    commu             = dump.add_argument("--dump-raw-communities", action="store_true")
    commu.help        = 'Text file containing the raw communities clustering'
    
    sem_commu         = dump.add_argument("--dump-semantic-communities", action="store_true")
    sem_commu.help    = 'Text file containing the raw clustering reconciled with SMV'
    
    stats             = dump.add_argument("--dump-stats", action="store_true")
    stats.help        = 'CSV file containing the evolution of modularity and #commu.'
    
    stats             = dump.add_argument("--dump-json-cluster-graph", action="store_true")
    stats.help        = 'JSON file containing a representation of the cluster graph'
    
    
    ################## SHOW COMMAND ###########################################
    show              = args.add_argument_group("Visualization")
    show.help         = "Generate some visulization artefacts"
    
    dimacs            = show.add_argument("--show-vig", action="store_true")
    dimacs.help       = 'Generate the complete VIG for each instance' 
    
    cluster           = show.add_argument("--show-cluster-graph", action="store_true")
    cluster.help      = 'Generate a cluster graph, where communities are merged' 
    
    d3_cluster        = show.add_argument("--show-d3-cluster-graph", action="store_true")
    d3_cluster.help   = 'Generates a d3 graph based visualisation of the problem' 
    
    time_table        = show.add_argument("--show-time-table", action="store_true")
    time_table.help   = 'Generates a d3 time/table based visualisation of the problem (very useful!)'
    
    fca_concepts      = show.add_argument("--show-formal-concepts", action="store_true")
    fca_concepts.help = 'Shows the concepts that could be mined in each of the communities using formal concept analysis'
    
    clouds            = show.add_argument("--show-clouds", action="store_true")
    clouds.help       = 'Generate a word cloud for each community' 
    
    stats             = show.add_argument("--show-stats", action="store_true")
    stats.help        = 'Plot the evolution of modularity and #commu.' 
    
    ################## MINE COMMAND ###########################################
    mine              = args.add_argument_group("Mining")
    mine.help         = "Mines the semantic information (SMV identifiers)"
    
    patterns          = mine.add_argument("--mine-patterns", action="store_true")
    patterns.help     = 'Mine frequently occuring *patterns* with RELIM'  
    
    sequences         = mine.add_argument("--mine-sequences", action="store_true")
    sequences.help    = 'Mine frequently occuring *sequences* with "a priori"' 
    
    return args

def parse_args():
    args              = arguments()
    parsed            = args.parse_args()
    
    if parsed.verbose:
        global __VERBOSE
        __VERBOSE = True
    
    return parsed

def do_nothing_flags():
    flags = namedtuple('Flags', 'dump_cnf dump_mapping dump_communities dump_raw_communities dump_semantic_communities dump_stats '
                              + 'show_vig show_cluster_graph show_d3_cluster_graph showw_time_table show_formal_concepts show_clouds show_stats '
                              + 'mine_patterns mine_sequences')
    return flags(False, False, False, False, False, False, False, False, False, False, False, False, False, False, False)
    
def log_verbose(func):
    '''
    Decorator that logs the call to a function if it is called with a keyword
    flags which has an attribute 'verbose' set to true.
    '''
    def logger(*args, **kwargs):
        global __VERBOSE
        
        if __VERBOSE:
            print("{} | {} {}".format(func.__name__, *args, **kwargs))
        return func(*args, **kwargs)
    return logger
