# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

from simulation.aivika.modeler.results import *
from simulation.aivika.modeler.util import *
from simulation.aivika.modeler.experiment.base.types import *

class FinalTableView(BasicExperimentView):
    """It saves the simulation results in final time points for all runs in CSV file."""

    def __init__(self,
                 title = None,
                 descr = None,
                 series = None,
                 separator = None,
                 run_text = None,
                 link_text = None):
        """Initializes a new instance."""
        BasicExperimentView.__init__(self)
        self.title = title
        self.descr = descr
        self.series = series
        self.separator = separator
        self.run_text = run_text
        self.link_text = link_text

    def write(self, file, indent = ''):
        """Write the view definition in the file."""
        file.write('defaultFinalTableView')
        fields = {}
        if not (self.title is None):
            func = lambda file, indent: file.write(encode_str(self.title))
            fields['finalTableTitle'] = func
        if not (self.descr is None):
            func = lambda file, indent: file.write(encode_str(self.descr))
            fields['finalTableDescription'] = func
        if not (self.series is None):
            func = lambda file, indent: write_sources(self.series, file, indent + '  ')
            fields['finalTableSeries'] = func
        if not (self.separator is None):
            func = lambda file, indent: file.write(encode_str(self.separator))
            fields['finalTableSeparator'] = func
        if not (self.run_text is None):
            func = lambda file, indent: file.write(encode_str(self.run_text))
            fields['finalTableRunText'] = func
        if not (self.link_text is None):
            func = lambda file, indent: file.write(encode_str(self.link_text))
            fields['finalTableLinkText'] = func
        write_record_fields(fields, file, indent + '  ')
