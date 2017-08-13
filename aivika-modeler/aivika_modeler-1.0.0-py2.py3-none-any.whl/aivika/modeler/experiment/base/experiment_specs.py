# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

from simulation.aivika.modeler.util import *
from simulation.aivika.modeler.experiment.base.types import *

class ExperimentSpecsView(BasicExperimentView):
    """It shows the experiment specs."""

    def __init__(self,
                 title = None,
                 descr = None):
        """Initializes a new instance."""
        BasicExperimentView.__init__(self)
        self.title = title
        self.descr = descr

    def write(self, file, indent = ''):
        """Write the view definition in the file."""
        file.write('defaultExperimentSpecsView')
        fields = {}
        if not (self.title is None):
            func = lambda file, indent: file.write(encode_str(self.title))
            fields['experimentSpecsTitle'] = func
        if not (self.descr is None):
            func = lambda file, indent: file.write(encode_str(self.descr))
            fields['experimentSpecsDescription'] = func
        write_record_fields(fields, file, indent + '  ')
