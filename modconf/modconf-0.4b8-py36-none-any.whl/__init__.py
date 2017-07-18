__version__ = '0.4b8'

import sys

def import_conf(name, folder=None):
    if folder:
        sys.path.insert(0, folder)
    
    try:
        m = __import__(name, fromlist='*')
    except:
        print('modconf folder={}'.format(repr(folder)))
        raise
    finally:
        if folder:
            sys.path.pop(0)

    return m

def import_class(mod_name, class_name, args, kwargs={}, folder=None):
    mod = import_conf(mod_name, folder)
    cls = mod.__dict__[class_name]
    cls.prepare(*args, **kwargs)
    return cls



