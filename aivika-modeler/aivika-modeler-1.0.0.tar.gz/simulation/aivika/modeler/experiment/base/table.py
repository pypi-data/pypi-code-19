# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

from simulation.aivika.modeler.results import *
from simulation.aivika.modeler.util import *
from simulation.aivika.modeler.experiment.base.types import *

class TableView(BasicExperimentView):
    """It saves the simulation results in CSV file(s)."""

    def __init__(self,
                 title = None,
                 descr = None,
                 series = None,
                 separator = None,
                 link_text = None,
                 run_link_text = None):
        """Initializes a new instance."""
        BasicExperimentView.__init__(self)
        self.title = title
        self.descr = descr
        self.series = series
        self.separator = separator
        self.link_text = link_text
        self.run_link_text = run_link_text

    def write(self, file, indent = ''):
        """Write the view definition in the file."""
        file.write('defaultTableView')
        fields = {}
        if not (self.title is None):
            func = lambda file, indent: file.write(encode_str(self.title))
            fields['tableTitle'] = func
        if not (self.descr is None):
            func = lambda file, indent: file.write(encode_str(self.descr))
            fields['tableDescription'] = func
        if not (self.series is None):
            func = lambda file, indent: write_sources(self.series, file, indent + '  ')
            fields['tableSeries'] = func
        if not (self.separator is None):
            func = lambda file, indent: file.write(encode_str(self.separator))
            fields['tableSeparator'] = func
        if not (self.link_text is None):
            func = lambda file, indent: file.write(encode_str(self.link_text))
            fields['tableLinkText'] = func
        if not (self.run_link_text is None):
            func = lambda file, indent: file.write(encode_str(self.run_link_text))
            fields['tableRunLinkText'] = func
        write_record_fields(fields, file, indent + '  ')
