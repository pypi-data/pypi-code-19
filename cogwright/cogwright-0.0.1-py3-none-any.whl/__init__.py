#!python
#-- cogwright.__init__

"""
"""


from .__version__ import __version__

import os as _os
if '__SETUP_PY__' in _os.environ and _os.environ['__SETUP_PY__'] == 'cogwright' :
    from .__main__ import command_line_parameters
    from .__main__ import cog
    from .__main__ import main


