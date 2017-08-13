# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

import os
import webbrowser

from simulation.aivika.modeler.util import *

class ExperimentException(Exception):
    """Raised when something is invalid when creating the experiment."""

    def __init__(self, message):
        """Initializes a new instance."""
        self.message = message

class Experiment:
    """The simulation experiment."""

    def __init__(self,
                 renderer,
                 run_count = '1',
                 title = None,
                 descr = None):
        """Initializes a new instance."""
        self._renderer = renderer
        self._path = get_experiment_path()
        self.run_count = run_count
        self.title = title
        self.descr = descr

    def get_path(self):
        """Return the experiment path."""
        return self._path

    def install(self, model):
        """Install the prerequisites."""
        self._renderer.install(model)
        model.add_package_import('aivika-experiment')
        model.add_extra_dep('aivika-experiment-5.0')
        if model.get_base_comp() is None:
            model.add_module_import('import Simulation.Aivika.Experiment')
        else:
            model.add_module_import('import Simulation.Aivika.Experiment.Trans')

    def write(self, file):
        """Write the experiment definition in the file."""
        indent = '  '
        file.write('experiment =\n')
        file.write(indent)
        self._write_def(file, indent)
        file.write('\n')
        file.write('\n')
        self._renderer.write(file, self)

    def _write_def(self, file, indent = ''):
        """Write the experiment definition code in the file."""
        fields = {}
        fields['experimentSpecs'] = lambda file, indent: file.write('specs')
        fields['experimentRunCount'] = lambda file, indent: file.write(str(self.run_count))
        if not (self.title is None):
            func = lambda file, indent: file.write(encode_str(self.title))
            fields['experimentTitle'] = func
        if not (self.descr is None):
            func = lambda file, indent: file.write(encode_str(self.descr))
            fields['experimentDescription'] = func
        file.write('defaultExperiment')
        write_record_fields(fields, file, indent + '  ')

    def open(self):
        """Open the experiment results in the browser."""
        url = 'file://' + self.get_path() + os.sep + 'index.html'
        webbrowser.open(url)

def get_experiment_path():
    """Get the experiment directory path."""
    cwd = os.getcwd()
    basedir = cwd + os.sep + 'experiment'
    counter = 1
    while True:
        if counter == 1:
            dirname = basedir
        else:
            dirname = basedir + '(' + str(counter) + ')'
        counter += 1
        if not os.path.exists(dirname):
            return dirname
