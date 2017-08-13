# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

from simulation.aivika.modeler.results import *
from simulation.aivika.modeler.util import *
from simulation.aivika.modeler.experiment.base.types import *

class XYChartView(BasicExperimentView):
    """It plots the XY Chart chart for all simulation runs."""

    def __init__(self,
                 title = None,
                 descr = None,
                 width = None,
                 height = None,
                 x_series = None,
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
        self.x_series = x_series
        self.left_y_series = left_y_series
        self.right_y_series = right_y_series
        self.plot_title = plot_title
        self.run_plot_title = run_plot_title

    def write(self, file, indent = ''):
        """Write the view definition in the file."""
        file.write('defaultXYChartView')
        fields = {}
        if not (self.title is None):
            func = lambda file, indent: file.write(encode_str(self.title))
            fields['xyChartTitle'] = func
        if not (self.descr is None):
            func = lambda file, indent: file.write(encode_str(self.descr))
            fields['xyChartDescription'] = func
        if not (self.width is None):
            func = lambda file, indent: file.write(str(self.width))
            fields['xyChartWidth'] = func
        if not (self.height is None):
            func = lambda file, indent: file.write(str(self.height))
            fields['xyChartHeight'] = func
        if not (self.x_series is None):
            func = lambda file, indent: write_sources([self.x_series], file, indent + '  ')
            fields['xyChartXSeries'] = func
        if not (self.left_y_series is None):
            func = lambda file, indent: write_sources(self.left_y_series, file, indent + '  ')
            fields['xyChartLeftYSeries'] = func
        if not (self.right_y_series is None):
            func = lambda file, indent: write_sources(self.right_y_series, file, indent + '  ')
            fields['xyChartRightYSeries'] = func
        if not (self.plot_title is None):
            func = lambda file, indent: file.write(encode_str(self.plot_title))
            fields['xyChartPlotTitle'] = func
        if not (self.run_plot_title is None):
            func = lambda file, indent: file.write(encode_str(self.run_plot_title))
            fields['xyChartRunPlotTitle'] = func
        write_record_fields(fields, file, indent + '  ')
