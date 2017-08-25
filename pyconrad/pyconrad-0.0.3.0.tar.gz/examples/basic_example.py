
# Copyright (C) 2010-2017 - Andreas Maier
# CONRAD is developed as an Open Source project under the GNU General Public License (GPL-3.0)

from pyconrad import PyConrad

# PyConrad is a singleton class
pyconrad = PyConrad()
# setup PyConrad
pyconrad.setup()
# Optional parameters for Java Virtual Machine RAM and own Java projects
# pyconrad.setup(max_ram = '8G', min_ram= '500M', dev_dirs=['path/to/project/with/own/java/classes']
pyconrad.start_conrad()

# Create Phantom (edu.stanford.rsl.tutorial.phantoms.MickeyMouseGrid2D)
phantom = pyconrad.classes.stanford.rsl.tutorial.phantoms.MickeyMouseGrid2D(300, 300)
# Access more easily using imports
pyconrad.add_import('edu.stanford.rsl.tutorial.phantoms')
phantom2 = pyconrad['MickeyMouseGrid2D'](200,200)

# Use Java method of class MickeyMouseGrid2D
phantom.show()


