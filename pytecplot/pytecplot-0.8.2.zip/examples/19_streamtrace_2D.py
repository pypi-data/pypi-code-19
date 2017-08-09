import tecplot
import os

examples_dir = tecplot.session.tecplot_examples_directory()
datafile = os.path.join(examples_dir, '2D', 'VortexShedding.lpk')
tecplot.load_layout(datafile)


frame = tecplot.active_frame()
frame.plot_type = tecplot.constant.PlotType.Cartesian2D
plot = frame.plot()
ds = frame.dataset

plot.vector.u_variable = ds.variable('U(M/S)')
plot.vector.v_variable = ds.variable('V(M/S)')

strace = plot.streamtraces

strace.add_rake([-0.002, 0.002],[-0.002, -0.002], tecplot.constant.Streamtrace.TwoDLine)
strace.show_arrows = False
strace.line_thickness = .4
plot.show_streamtraces = True

# Remove countour lines setup in LPK
plot.fieldmap(0).contour.contour_type = tecplot.constant.ContourType.Flood


# Delete textboxes setup for LPK
for txt in frame.texts():
    frame.delete_text(txt)

tecplot.export.save_png('streamtrace_2D.png', 600, supersample=4)
