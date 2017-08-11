'''
Don't pay any attention to this module, it is only present here for me to fiddle
with the tool while I'm developing it in my IDE
'''
import pynusmv_community.cmdline as cmdline
import pynusmv_community.main    as main
 
        
if __name__ == '__main__':
    model= "NMH21_2"
    path = "/Users/user/Documents/EXPERIMENTS/bmc_data/models/nameche" 
    prop = ""
    #prop = "G (v211.U_KM_07M.st = l -> (v211.U_07M_09M.st = l xor v211.U_07M_04M.st = l))"
    
    #model= "philo_9"                                  
    #path = "/Users/user/Documents/EXPERIMENTS/bmc_data/models"
    #prop = "F G (p1.waiting -> F !p1.waiting)"
    
    #model= "hard_twin"                                  
    #path = "/Users/user/Documents/EXPERIMENTS/bmc_data/models"
    #prop = '''G ! ( (test.a.c.value + test.b.c.value + test.c.c.value + test.d.c.value + test.e.c.value + test.f.c.value + test.g.c.value = 2 )
    #    & (twin.a.c.value + twin.b.c.value + twin.c.c.value + twin.d.c.value + twin.e.c.value + twin.f.c.value + twin.g.c.value = 0) )'''
    
    cmdline.__VERBOSE = True
    
    args     = cmdline.arguments().parse_args([
        '--path', path, '-K', '3',#'--formula', prop, '-k', '20', '-K', '20',
        #'--dump-raw-communities',
        #'--show-vig',
        '--mine-patterns', 
        #'--mine-sequences',
        #'--show-cluster-graph',
        #'--dump-json-cluster-graph',
        #'--dump-stats',
        #'--show-stats',
        #'--show-d3-cluster-graph', ## kinda useless
        #'--show-time-table',
        #'--show-formal-concepts',
        model
        ])
    
                                                                                  
    rng  = range(args.min_bound, 1+args.max_bound)
    main.process(args.path, args.model, args.formula, rng, args)
