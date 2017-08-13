# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

from simulation.aivika.modeler.results import *
from simulation.aivika.modeler.util import *
from simulation.aivika.modeler.experiment.base.types import *

class TimingStatsView(BasicExperimentView):
    """It gathers the time-persistent statistics for reach simulation run."""

    def __init__(self,
                 title = None,
                 run_title = None,
                 descr = None,
                 series = None):
        """Initializes a new instance."""
        BasicExperimentView.__init__(self)
        self.title = title
        self.run_title = run_title
        self.descr = descr
        self.series = series

    def write(self, file, indent = ''):
        """Write the view definition in the file."""
        file.write('defaultTimingStatsView')
        fields = {}
        if not (self.title is None):
            func = lambda file, indent: file.write(encode_str(self.title))
            fields['timingStatsTitle'] = func
        if not (self.run_title is None):
            func = lambda file, indent: file.write(encode_str(self.run_title))
            fields['timingStatsRunTitle'] = func
        if not (self.descr is None):
            func = lambda file, indent: file.write(encode_str(self.descr))
            fields['timingStatsDescription'] = func
        if not (self.series is None):
            func = lambda file, indent: write_sources(self.series, file, indent + '  ')
            fields['timingStatsSeries'] = func
        write_record_fields(fields, file, indent + '  ')
