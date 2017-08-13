# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

from simulation.aivika.modeler.results import *
from simulation.aivika.modeler.util import *
from simulation.aivika.modeler.experiment.base.types import *

class FinalStatsView(BasicExperimentView):
    """It gathers the observation statistics in final time points."""

    def __init__(self,
                 title = None,
                 descr = None,
                 series = None):
        """Initializes a new instance."""
        BasicExperimentView.__init__(self)
        self.title = title
        self.descr = descr
        self.series = series

    def write(self, file, indent = ''):
        """Write the view definition in the file."""
        file.write('defaultFinalStatsView')
        fields = {}
        if not (self.title is None):
            func = lambda file, indent: file.write(encode_str(self.title))
            fields['finalStatsTitle'] = func
        if not (self.descr is None):
            func = lambda file, indent: file.write(encode_str(self.descr))
            fields['finalStatsDescription'] = func
        if not (self.series is None):
            func = lambda file, indent: write_sources(self.series, file, indent + '  ')
            fields['finalStatsSeries'] = func
        write_record_fields(fields, file, indent + '  ')
