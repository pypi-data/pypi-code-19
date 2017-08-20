"""
=============================
Use tkinter to get user input
=============================

This example creates a window with as many inputs as
keys in a dictionary.
"""

#########################################
# This section adds paths for modules being developped on the same machine
# and never installed. I could use a virtual environment
# but it is uneasy on a daily basis.

import os
import sys
this = os.path.abspath(os.path.dirname(__file__))
if "tkinterquickhelper" in this:
    this = this.split("tkinterquickhelper")[0].rstrip("\\/")
for module in ["pyquickhelper", "tkinterquickhelper"]:
    try:
        exec("import %s" % module)
    except ImportError:
        p = os.path.join(this, module, "src")
        print("add path", p)
        sys.path.append(p)
        exec("import %s" % module)

###############################
from tkinterquickhelper.funcwin import open_window_params

###############################
params = {"user": os.environ.get("USERNAME", os.environ.get(
    "HOSTNAME", "unknown")), "password": ""}

###############################
newparams = open_window_params(params, title="try the password *",
                               help_string="unit test", key_save="my_key")

###############################
print(newparams)
