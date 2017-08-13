# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

from simulation.aivika.modeler.results import *
from simulation.aivika.modeler.util import *
from simulation.aivika.modeler.experiment.base.types import *

class FinalHistogramView(BasicExperimentView):
    """It plots the histogram for the specified series in final time points collected from different simulation runs."""

    def __init__(self,
                 title = None,
                 descr = None,
                 width = None,
                 height = None,
                 series = None,
                 plot_title = None):
        """Initializes a new instance."""
        BasicExperimentView.__init__(self)
        self.title = title
        self.descr = descr
        self.width = width
        self.height = height
        self.series = series
        self.plot_title = plot_title

    def write(self, file, indent = ''):
        """Write the view definition in the file."""
        file.write('defaultFinalHistogramView')
        fields = {}
        if not (self.title is None):
            func = lambda file, indent: file.write(encode_str(self.title))
            fields['finalHistogramTitle'] = func
        if not (self.descr is None):
            func = lambda file, indent: file.write(encode_str(self.descr))
            fields['finalHistogramDescription'] = func
        if not (self.width is None):
            func = lambda file, indent: file.write(str(self.width))
            fields['finalHistogramWidth'] = func
        if not (self.height is None):
            func = lambda file, indent: file.write(str(self.height))
            fields['finalHistogramHeight'] = func
        if not (self.series is None):
            func = lambda file, indent: write_sources(self.series, file, indent + '  ')
            fields['finalHistogramSeries'] = func
        if not (self.plot_title is None):
            func = lambda file, indent: file.write(encode_str(self.plot_title))
            fields['finalHistogramPlotTitle'] = func
        write_record_fields(fields, file, indent + '  ')
