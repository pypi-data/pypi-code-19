# -*- coding: utf-8 -*-
import yaml
import os
import sys
from time import time
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
from .runs import Runs

from logcon import log
import logging

class Optimiser():
    """ 
    wrapper for hyperopt optimisation
    
        simplified search space (in addition to hyperopt search format)
            max_depth=[8,10],       # int
            color=["r", "g", "b"],  # categoric
            normalize=[True,False], # bool
            c=[1., 5],              # float
            classifier="SVM"        # constant
            x=hp.lognormal("x",0,1) # any hyperopt search format
                   
        before each iteration
            log parameters
        
        after each iteration
            log result
            save in runs object so resilient to crash
            
        after optimisation
            use runs object to report results and charts
    """
    def __init__(self, folder="optimise", mode="w", maximise=False,
                 trials=Trials()):
        """
        folder for logging
        mode a=append, w=write
        maximise multiplies loss by -1 to allow maximise function
        trials used by hyperopt to record space searched
        """
        # int params need rounding due to hyperopt bug
        self.intparams = []
        
        self.maximise = maximise
        if self.maximise:
            log.warning("Hyperopt minimises. To maximise score it will be shown "\
                "as negative except in charts")
        
        self.trials = Trials()
        self.runs = Runs(folder, mode)
    
    def convert(self, space):
        """ converts simple search space to hyperopt format
        """
        for k, v in list(space.items()):
            # hypreopt expression or constant
            if not isinstance(v, list):
                continue
            
            # categoric and bool
            if len(v)>2 \
                    or any(isinstance(v, str) for v in v) \
                    or any(isinstance(v, bool) for v in v):
                space[k] = hp.choice(k, v)
            # integer range
            elif all(isinstance(v, int) for v in v):
                space[k] = hp.quniform(k, v[0]-.5, v[1]+.5, 1)
                self.intparams.append(k)
            # float range
            else:
                space[k] = hp.uniform(k, v[0], v[1])
            
    def make_target(self, func, inputs):
        """ wrap func with pre and post processing
            func signature: score=func(**params)
        """
        def target(params):
            """ called by optimiser for each iteration
            """
            starttime = time()
            
            # report params
            if self.verbose >= 20:
                paramsout = ', '.join("{!s}={!r}".format(k,v) 
                                    for (k,v) in params.items())
                log.info(f"[{len(self.trials)}] {paramsout}")

            # hyperopt integers stored as float (probably a bug)
            for k in self.intparams:
                params[k] = int(round(params[k]))
            
            # add fixed inputs such as x, y
            params.update(inputs)
            
            #########################################
            loss = func(params)
            #########################################

            # exclude fixed inputs from reporting or trials object
            params = {k:v for k,v in params.items() if k not in inputs}
            
            if self.maximise:
                loss = -loss
            
            # report score
            if self.verbose >= 20:
                log.info("****** %s ******"%loss)

            # add iteration to trials object
            params.update(loss=loss,
                          status=STATUS_OK, 
                          elapsed=time()-starttime)

            # save results so resilient to crash
            self.runs.append(params)
            
            return params
        
        return target

    def optimise(self, func, evals=1, verbose=20, clear=True,
                         inputs=dict(), **hpargs):
        """
        minimise func by varying hyperparameters
        
        func=signature func(params). returns loss to be minimised
        evals=additional func evaluations
                ignored if hpargs["max_evals"]
                hpargs["max_evals"] includes previous trials
        inputs=constants passed to each iteration e.g. x, y
                optional as can be set in class or in notebook
        hpargs["space"]=simplified hyperopt space to be converted to hp format
        hpargs passed to hyperopt
        """
        log.getLogger("hyperopt.tpe").setLevel(logging.WARNING)
        self.verbose = verbose
        
        self.trials = hpargs.get("trials", self.trials) 
        hpargs["trials"] = self.trials
        
        hpargs.setdefault("max_evals", len(self.trials) + evals)
        hpargs.setdefault("algo", tpe.suggest)
        self.convert(hpargs["space"])
        target = self.make_target(func, inputs)

        try:
            fmin(target, **hpargs)
        except KeyboardInterrupt:
            pass
        
        # output results
        self.runs.show_best(clear=clear)
        self.runs.plot()

    def optimise_by_parameter(self,  *args, **kwargs):
        """ univariate runs of params """
        for k,v in kwargs["space"].items():
            if k in ["name"]:
                continue
            kwargs["trials"] = Trials()
            kwargs["space"] = {k:v}
            self.optimise(*args, **kwargs)

###############################################################
   
def get_space(key, folder=None):
    """ lookup space using key in search.yaml
    """
    for path in [folder] + sys.path + \
                    [os.path.join(sys.prefix, "etc", "optimise"), 
                     os.path.join(os.pardir, os.path.dirname(__file__))]:
        try:
            space = yaml.load(open(os.path.join(path, "search.yaml")))[key]
            space["name"] = key
            break
        except:
            continue

    return space
    
def get_params_range(params, excluded=None, spread=None):
    """ gets params space in range
        spread is either side of params.values()
        e.g. v=10, spread=[.9, 1.1] ==> v=[9, 11]
    """
    if spread is None:
        spread = [.9, 1.1]
    for k,v in params.items():
        if k in excluded:
            continue
        if isinstance(v, float):
            params[k] = [v*spread[0], v*spread[1]]
        elif isinstance(v, int):
            params[k] = [round(v*spread[0]), round(v*spread[1])]