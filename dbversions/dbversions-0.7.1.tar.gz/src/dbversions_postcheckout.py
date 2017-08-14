#!/usr/bin/env python

import sys

prevHead = sys.argv[1]
newHead = sys.argv[2]
branchCheckout = int(sys.argv[3])

if (branchCheckout == 1) and not (prevHead == newHead):
    
    import os
    from dbversions import Config, DBConfig
    
    projectpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__))+'/../../')
    cfg = Config(projectpath)
    dbconfig = DBConfig(cfg)
    dbconfig.checkout()
    
else:
    pass