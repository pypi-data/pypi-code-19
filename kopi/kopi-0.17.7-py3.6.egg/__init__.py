#! /usr/local/bin/python3
"""
pplot
=====
[lcchen, leechuin@gmail.com, leechuin@yamanashi.ac.jp]
Plot 2D graph in pdf format
Reference: pyplot, R, ggplot

Objective:
To provide a user friendly interface
to create common publication quality graphs in pdf.

The setting can be done by modifying the
style settings in the cson file
(coffee script object notation).

Kopi is the malay word for coffee. The term is commonly used
in Malaysia and Singapore to refer a locally brewed coffee.

	========
    Example
	========
	#!python3
	import numpy as np
	import kopi as k

	x = [1,2,3]
	y = [1,4,9]
	k.plot(x,y)

	# or
	x = np.array(x)
	y = x**2
	k.plot(x,y)

	# To plot multiple curve in one graph
	#, put the numpy array in list.
	k.plot([x, x, x], [x, y, x**3])

	# To plot multiple plot in one graph use mplot.
	# It is a little tricky.
	# Bundle the list in a global list
	k.mplot([[x,y],# 1st plot
		[x,x**3],# 2nd plot
		[[x,x],[y,x**3]]# 3rd plot with two curves
		])

	# sugar and milk:
	sugar : plot style dictionary to overwrite the content in
			coffee (plot style .cson file )
	milk :	plot style dictionary to overwrite the content in
			morecoffee (multi plot style .cson file )

"""
__all__ = ["plot", "image","polar","mplot", "brew"]
__what__ = "I have no idea"
from .main import *
from .brewcson import brew
from . import __version__ as ver
__version__ = ver.__version__
