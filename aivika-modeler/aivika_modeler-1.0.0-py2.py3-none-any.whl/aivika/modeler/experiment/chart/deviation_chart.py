# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

from simulation.aivika.modeler.results import *
from simulation.aivika.modeler.util import *
from simulation.aivika.modeler.experiment.base.types import *

class DeviationChartView(BasicExperimentView):
    """It plots the Deviation Chart with the confidence interval by rule 3 sigma."""

    def __init__(self,
                 title = None,
                 descr = None,
                 width = None,
                 height = None,
                 left_y_series = None,
                 right_y_series = None,
                 plot_title = None):
        """Initializes a new instance."""
        BasicExperimentView.__init__(self)
        self.title = title
        self.descr = descr
        self.width = width
        self.height = height
        self.left_y_series = left_y_series
        self.right_y_series = right_y_series
        self.plot_title = plot_title

    def write(self, file, indent = ''):
        """Write the view definition in the file."""
        file.write('defaultDeviationChartView')
        fields = {}
        if not (self.title is None):
            func = lambda file, indent: file.write(encode_str(self.title))
            fields['deviationChartTitle'] = func
        if not (self.descr is None):
            func = lambda file, indent: file.write(encode_str(self.descr))
            fields['deviationChartDescription'] = func
        if not (self.width is None):
            func = lambda file, indent: file.write(str(self.width))
            fields['deviationChartWidth'] = func
        if not (self.height is None):
            func = lambda file, indent: file.write(str(self.height))
            fields['deviationChartHeight'] = func
        if not (self.left_y_series is None):
            func = lambda file, indent: write_sources(self.left_y_series, file, indent + '  ')
            fields['deviationChartLeftYSeries'] = func
        if not (self.right_y_series is None):
            func = lambda file, indent: write_sources(self.right_y_series, file, indent + '  ')
            fields['deviationChartRightYSeries'] = func
        if not (self.plot_title is None):
            func = lambda file, indent: file.write(encode_str(self.plot_title))
            fields['deviationChartPlotTitle'] = func
        write_record_fields(fields, file, indent + '  ')
