# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

from simulation.aivika.modeler.util import *

class ExperimentRenderer:
    """The simulation experiment renderer."""

    def __init__(self, views):
        """Initializes a new instance."""
        self._views = views

    def install(self, model):
        """Install the prerequisites."""
        for view in self._views:
            view.install(model)
        model.add_package_import('aivika-experiment')
        model.add_extra_dep('aivika-experiment-5.0')
        if model.get_base_comp() is None:
            model.add_module_import('import Simulation.Aivika.Experiment')
        else:
            model.add_module_import('import Simulation.Aivika.Experiment.Trans')

    def _write_generators(self, file):
        """Write the generators."""
        func = lambda file, item, indent: self._write_view(file, item, indent)
        indent = '  '
        file.write('generators =\n')
        file.write(indent)
        write_list(func, self._views, file, indent)
        file.write('\n')

    def _write_view(self, file, view, indent):
        """Write the view output."""
        file.write('outputView $ ')
        view.write(file, indent)

class ChartingExperimentRenderer(ExperimentRenderer):
    """The simulation experiment renderer that creates charts."""

    def __init__(self, views):
        """Initializes a new instance."""
        ExperimentRenderer.__init__(self, views)

    def install(self, model):
        """Install the prerequisites."""
        ExperimentRenderer.install(self, model)
        model.add_package_import('Chart')
        model.add_package_import('aivika-experiment-chart')
        model.add_extra_dep('aivika-experiment-chart-5.0')
        if model.get_base_comp() is None:
            model.add_module_import('import Simulation.Aivika.Experiment.Chart')
        else:
            raise ExperimentException('No support for the generalized version')

    def _write_generators(self, file):
        """Write the generators."""
        file.write('generators :: ChartRendering r => [WebPageGenerator r]\n')
        ExperimentRenderer._write_generators(self, file)

class ExperimentRendererUsingDiagrams(ChartingExperimentRenderer):
    """The simulation experiment renderer that uses Diagrams."""

    def __init__(self, views):
        """Initializes a new instance."""
        ChartingExperimentRenderer.__init__(self, views)

    def install(self, model):
        """Install the prerequisites."""
        ChartingExperimentRenderer.install(self, model)
        model.add_package_import('Chart-diagrams')
        model.add_package_import('aivika-experiment-diagrams')
        model.add_extra_dep('aivika-experiment-diagrams-5.0')
        if model.get_base_comp() is None:
            model.add_module_import('import Simulation.Aivika.Experiment.Chart.Backend.Diagrams')
            model.add_module_import('import Graphics.Rendering.Chart.Backend.Diagrams')
        else:
            raise ExperimentException('No support for the generalized version')

    def write(self, file, experiment):
        """Write the code that runs the simulation experiment."""
        self._write_generators(file)
        file.write('\n')
        file.write('main =\n')
        file.write('  do putStrLn "Loading SVG fonts..."\n')
        file.write('     fonts <- loadCommonFonts\n')
        file.write('     putStrLn "Loaded."\n')
        file.write('     putStrLn "Started running the simulation and saving the results..."\n')
        file.write('     let renderer = DiagramsRenderer SVG (return fonts)\n')
        file.write('         path     = WritableFilePath ' + encode_str(experiment.get_path()) + '\n')
        file.write('     runExperimentParallel experiment generators (WebPageRenderer renderer path) model\n')
