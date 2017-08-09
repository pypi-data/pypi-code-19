from os import path
import numpy as np

import tecplot as tp
from tecplot.constant import PlotType

exdir = tp.session.tecplot_examples_directory()
datafile = path.join(exdir, '3D_Volume', 'waveintensity.plt')
dataset = tp.data.load_tecplot(datafile)

fr = tp.active_frame()
plot = fr.plot(PlotType.Cartesian2D)
plot.activate()
plot.show_contour = True

plot.contour(0).legend.show = False

xvar = plot.axes.x_axis.variable
yvar = plot.axes.y_axis.variable

# set the y axis maximum to the data's maximum
plot.axes.y_axis.max = dataset.zone(0).values(yvar.index).max

# export image of original data
tp.export.save_png('interpolate_2d_source.png', 600, supersample=3)

# use the first zone as the source, and get the range of (x, y)
srczone = dataset.zone(0)
xmin, xmax = srczone.values(xvar.index).minmax
ymin, ymax = srczone.values(yvar.index).minmax

# create new zone with a coarse grid
# onto which we will interpolate from the source zone
xpoints = 50
ypoints = 30
newzone = dataset.add_ordered_zone('Interpolated', (xpoints, ypoints))

# setup the (x, y) positions of the new grid
xx = np.linspace(xmin, xmax, xpoints)
yy = np.linspace(ymin, ymax, ypoints)
YY, XX = np.meshgrid(yy, xx, indexing='ij')
newzone.values(xvar.index)[:] = XX.ravel()
newzone.values(yvar.index)[:] = YY.ravel()

# perform linear interpolation from the source to the new zone
tp.data.operate.interpolate_linear(newzone, srczone)

# show the new zone's data, hide the source
plot.fieldmap(newzone).show = True
plot.fieldmap(srczone).show = False

# export image of interpolated data
tp.export.save_png('interpolate_linear_2d_dest.png', 600, supersample=3)
