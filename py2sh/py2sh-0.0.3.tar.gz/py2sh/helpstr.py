import inspect
def helpcomponents_f(f):
    argnames, varargs, kwargnames, defaults = inspect.getargspec(f) 
    if defaults:                                                    
        help_args = argnames[:-len(defaults)]                       
    elif argnames:                                                  
        help_args = argnames                                        
    else:                                                           
        help_args = []                                              
                                                                    
    if varargs:                                                     
        help_args.append('<arg>, ...')                              
                                                                    
    if defaults and argnames:                                       
        help_kwargs = zip(argnames[-len(defaults):],defaults)
    else:                                                           
        help_kwargs = []                                            

    if kwargnames:
        help_kwargs.append(('<kwarg>','<val>,...'))

    return help_args, help_kwargs 

def helpstr(mainf, *fs):
    help_args, help_kwargs = helpcomponents_f(mainf)
    for f in fs:
        hargs, hkwargs = helpcomponents_f(f)
        help_args.extend(hargs)
        help_kwargs.extend(hkwargs)
    return help_args, help_kwargs

