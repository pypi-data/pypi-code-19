import os
import time


def filterbymtime(filepath, beforehours,extension_tuple):
    return os.path.getmtime(filepath) <= time.time()-beforehours*60*60 \
            and filepath.endswith(extension_tuple)
