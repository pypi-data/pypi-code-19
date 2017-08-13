# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

from simulation.aivika.modeler import *

class BasicExperimentView:
    """It shows the experiment specs."""

    def __init__(self):
        """Initializes a new instance."""

    def install(self, model):
        """Install the prerequisites."""
        model.add_package_import('aivika-experiment')
        model.add_extra_dep('aivika-experiment-5.0')
        if model.get_base_comp() is None:
            model.add_module_import('import Simulation.Aivika.Experiment.Base')
        else:
            raise ExperimentException('No support for the generalized version')
