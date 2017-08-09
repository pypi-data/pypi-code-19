import logging
import os
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

import tecplot

examples_dir = tecplot.session.tecplot_examples_directory()
infile = os.path.join(examples_dir, '3D', 'JetSurface.lay')

tecplot.load_layout(infile)
tecplot.export.save_jpeg('jet_surface.jpeg', 600)
