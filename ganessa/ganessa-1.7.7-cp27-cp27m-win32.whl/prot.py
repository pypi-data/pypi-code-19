# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
import os.path
import os
from util import _add_dir_to_path

debuglevel = 0
path = ('C:\\Program Files (x86)\\Safege\\SafProdLicMgr',
        'C:\\Program Files\\Safege\\SafProdLicMgr',
        'C:\\Program Files\\Fichiers communs\\Safege', 
        'C:\\Program Files (x86)\\Safege', 
        'C:\\Program Files\\Safege', 
        'D:\\Program Files\\Safege\\SafProdLicMgr',
        'D:\\Program Files\\Safege')
f = 'ProtDLL.dll'

def _test_import():
    try:
        import _prot as _mod
        del _mod
        return True
    except ImportError:
        return False

# Recherche de la DLL par le PATH
for ndir in os.environ['path'].split(';'):
    if os.path.exists(os.path.join(ndir, f)):
        if debuglevel > 0: print(f + ' found in Path: ' + ndir)
        if _test_import(): break
        else: continue
else:
# Puis par la liste predefinie
    for ndir in path:
        if debuglevel > 1: print(' ... examining ' + ndir + '/' + f)
        if _add_dir_to_path(ndir, f): 
            if debuglevel > 0: print(' ... testing ' + ndir + '/' + f)
            if _test_import():
                if debuglevel > 0: print(f + ' responding from ' + ndir)
                break
            else:
                print(f + ' found in ' + ndir + ' but *NOT* responding')
                continue
    else:
    # On n'a pas trouve
        raise ImportError('Unable to find an adequate DLL: SafProdLicMgr/' + f)

try:
    import _prot
except ImportError:
    raise ImportError('DLL ' + f + ': not found or too old.\n')
else:
    init = _prot.init_prot
    config = _prot.config
    def _close(*args):
        global _prot
        try:
            text = 'Protection unloaded.'
            _prot.close_prot()
            del _prot
        except NameError:
            text = 'Protection already unloaded...'
        finally:
            if args and args[0]:
                print (text)
        return text
    import atexit
    atexit.register(_close)
    close = _close
    
