# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

from simulation.aivika.modeler.results import *
from simulation.aivika.modeler.util import *
from simulation.aivika.modeler.experiment.base.types import *

class TimeSeriesView(BasicExperimentView):
    """It plots the Time Series chart for all simulation runs."""

    def __init__(self,
                 title = None,
                 descr = None,
                 width = None,
                 height = None,
                 left_y_series = None,
                 right_y_series = None,
                 plot_title = None,
                 run_plot_title = None):
        """Initializes a new instance."""
        BasicExperimentView.__init__(self)
        self.title = title
        self.descr = descr
        self.width = width
        self.height = height
        self.left_y_series = left_y_series
        self.right_y_series = right_y_series
        self.plot_title = plot_title
        self.run_plot_title = run_plot_title

    def write(self, file, indent = ''):
        """Write the view definition in the file."""
        file.write('defaultTimeSeriesView')
        fields = {}
        if not (self.title is None):
            func = lambda file, indent: file.write(encode_str(self.title))
            fields['timeSeriesTitle'] = func
        if not (self.descr is None):
            func = lambda file, indent: file.write(encode_str(self.descr))
            fields['timeSeriesDescription'] = func
        if not (self.width is None):
            func = lambda file, indent: file.write(str(self.width))
            fields['timeSeriesWidth'] = func
        if not (self.height is None):
            func = lambda file, indent: file.write(str(self.height))
            fields['timeSeriesHeight'] = func
        if not (self.left_y_series is None):
            func = lambda file, indent: write_sources(self.left_y_series, file, indent + '  ')
            fields['timeSeriesLeftYSeries'] = func
        if not (self.right_y_series is None):
            func = lambda file, indent: write_sources(self.right_y_series, file, indent + '  ')
            fields['timeSeriesRightYSeries'] = func
        if not (self.plot_title is None):
            func = lambda file, indent: file.write(encode_str(self.plot_title))
            fields['timeSeriesPlotTitle'] = func
        if not (self.run_plot_title is None):
            func = lambda file, indent: file.write(encode_str(self.run_plot_title))
            fields['timeSeriesRunPlotTitle'] = func
        write_record_fields(fields, file, indent + '  ')
