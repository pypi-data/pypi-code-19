# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

import os

from simulation.aivika.modeler.model_project import *

class ModelException(Exception):
    """Raised when something is invalid when creating or processing the model."""

    def __init__(self, message):
        """Initializes a new instance."""
        self.message = message

class InvalidVariableException(ModelException):
    """Raised when the variable is invalid."""

    def __init__(self, message):
        """Initializes a new instance."""
        ModelException.__init__(self, message)

class Model:
    """The simulation model."""
    pass

class MainModel(Model):
    """The main simulation model."""

    def __init__(self, base_comp = None):
        """Initializes a new simulation model."""
        self._base_comp = base_comp
        self._pragmas = set()
        self._package_imports = set()
        self._package_locations = set()
        self._extra_deps = set()
        self._module_imports = set()
        self._actions = []
        self._sources = []
        self._var_names = set()
        self._lazy_var_names = set()
        self._ports = set()
        self._transact_types = set()
        self._add_defaults()

    def _add_defaults(self):
        """Add the defaults."""
        self._pragmas.add('{-# LANGUAGE RecursiveDo #-}')
        self._package_imports.add('aivika')
        self._package_imports.add('aivika-transformers')
        self._extra_deps.add('aivika-5.2')
        self._extra_deps.add('aivika-transformers-5.2')
        if self._base_comp is None:
            self._module_imports.add('import Simulation.Aivika')
        else:
            self._module_imports.add('import Simulation.Aivika.Trans')
        self._module_imports.add('import Data.Monoid')
        self._module_imports.add('import Data.Functor')
        self._module_imports.add('import Control.Arrow')
        self._module_imports.add('import Control.Monad')

    def get_main_model(self):
        """Return the main model."""
        return self

    def get_base_comp(self):
        """Return the basic computation type."""
        return self._base_comp

    def get_var_prefix(self):
        """Return the variable prefix."""
        return ''

    def is_source_prefix_mangled(self):
        """Whether the source name prefix is mangled."""
        return False

    def get_source_prefix(self):
        """Return the source name prefix."""
        return ''

    def add_pragma(self, pragma):
        """Add the specified pragma."""
        self._pragmas.add(pragma)

    def add_package_import(self, package):
        """Add the specified package to import."""
        self._package_imports.add(package)

    def add_package_location(self, package_location):
        """Add the specified package location."""
        self._package_locations.add(package_location)

    def add_extra_dep(self, extra_dep):
        """Add the specified extra dependency."""
        self._extra_deps.add(extra_dep)

    def add_module_import(self, module):
        """Add the specified module to import."""
        self._module_imports.add(module)

    def add_var(self, name, comp):
        """Add a new variable with the specified definition."""
        if name in self._var_names:
            raise InvalidVariableException('Variable ' + name + ' is already defined')
        elif name in self._lazy_var_names:
            action = name + ' <- ' + comp
            self._lazy_var_names.remove(name)
            self._var_names.add(name)
            self.add_action(action)
        else:
            action = name + ' <- ' + comp
            self._var_names.add(name)
            self.add_action(action)

    def add_lazy_var(self, name):
        """Add a new variable that will be defined lazily."""
        if name in self._var_names:
            raise InvalidVariableException('Variable ' + name + ' is already defined')
        elif name in self._lazy_var_names:
            raise InvalidVariableException('Variable ' + name + ' is already added as lazy')
        else:
            self._lazy_var_names.add(name)

    def add_action(self, action):
        """Add the specified action."""
        self._actions.append(action)

    def add_port(self, port):
        """Add the specified port for completeness test."""
        self._ports.add(port)

    def add_result_source(self, source):
        """Add the specified result source."""
        self._sources.append(source)

    def add_transact_type(self, transact_type):
        """Add the specified transact type."""
        self._transact_types.add(transact_type)

    def require_complete(self):
        """Require the model to be complete."""
        if len(self._lazy_var_names) > 0:
            for name in self._lazy_var_names:
                raise InvalidVariableException('Variable ' + name + ' is used but not defined')
        for port in self._ports:
            if not port.is_bound_to_input():
                raise InvalidVariableException('Variable ' + port.get_name() + ' must be bound to its input')
            if not port.is_bound_to_output():
                raise InvalidVariableException('Variable ' + port.get_name() + ' must be bound to its output')

    def run(self, specs, experiment = None, dirname = 'target'):
        """Generate and compile the project."""
        self.generate(specs = specs, experiment = experiment, dirname = dirname)
        cwd = os.getcwd()
        os.chdir(dirname)
        status = os.system('stack build')
        if status == 0:
            status = os.system('stack exec modeling-project-exe')
        os.chdir(cwd)
        if (status == 0) and (not (experiment is None)):
            experiment.open()
        return status

    def compile(self, specs, experiment = None, dirname = 'target'):
        """Generate and compile the project."""
        self.generate(specs = specs, experiment = experiment, dirname = dirname)
        cwd = os.getcwd()
        os.chdir(dirname)
        status = os.system('stack build')
        os.chdir(cwd)
        return status

    def generate(self, specs, experiment = None, dirname = 'target'):
        """Generate the project files."""
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        if not os.path.exists(dirname + '/app'):
            os.makedirs(dirname + '/app')
        if not os.path.exists(dirname + '/src'):
            os.makedirs(dirname + '/src')
        if not (experiment is None):
            experiment.install(self)
        self._generate_model(specs, experiment, dirname + '/app/Main.hs')
        generate_cabal_file_impl(self, dirname + '/modeling-project.cabal')
        generate_stack_file_impl(self, dirname + '/stack.yaml')
        generate_license_file_impl(dirname + '/LICENSE.txt')
        generate_readme_file_impl(dirname + '/README.md')
        generate_setup_file_impl(dirname + '/Setup.hs')
        generate_lib_file_impl(dirname + '/src/Lib.hs')

    def _generate_model(self, specs, experiment = None, filename = 'dist/app/Model.hs'):
        """Generate the model file."""
        with open(filename, "w") as file:
            self._write_model(file, specs, experiment = experiment)

    def _write_model(self, file, specs, experiment = None):
        """Write the model file."""
        self.require_complete()
        for pragma in self._pragmas:
            file.write(pragma)
            file.write('\n')
        if len(self._pragmas) > 0:
            file.write('\n')
        file.write('-- NOTE: This file was auto-generated by aivika-modeler 1.0\n')
        file.write('\n')
        for module_import in self._module_imports:
            file.write(module_import)
            file.write('\n')
        if len(self._module_imports) > 0:
            file.write('\n')
        file.write('specs =\n')
        specs.write(file, '  ')
        file.write('\n')
        self._write_transact_types(file)
        self._write_model_def(file)
        file.write('\n')
        if experiment is None:
            file.write('main =\n')
            file.write('  printSimulationResultsInStopTime\n')
            file.write('  printResultSourceInEnglish\n')
            file.write('  model specs\n')
            file.write('\n')
        else:
            experiment.write(file)
            file.write('\n')

    def _write_model_def(self, file):
        """Write the model definition in the file."""
        file.write('model =')
        file.write('\n')
        self._write_model_code(file, '  ')

    def _write_model_code(self, file, indent = ''):
        """Write the code in the file."""
        file.write(indent)
        file.write('mdo --')
        file.write('\n')
        indent2 = indent + '    '
        for action in self._actions:
            file.write(indent2)
            file.write(action)
            file.write('\n')
        file.write(indent2)
        file.write('return $\n')
        file.write(indent2)
        file.write('  results\n')
        self._write_sources(file, indent2 + '  ')
        file.write('\n')

    def _write_sources(self, file, indent):
        """Write the result source list in file."""
        file.write(indent)
        file.write('[')
        first = True
        for source in self._sources:
            if first:
                first = False
                file.write(source)
            else:
                file.write(',\n')
                file.write(indent)
                file.write(' ')
                file.write(source)
        file.write(']')

    def _write_transact_types(self, file):
        """Add the transact types."""
        for tp in self._transact_types:
            tp.write(file)
            file.write('\n')

class SubModel(Model):
    """The sub-model."""

    _next_id = 1

    def __init__(self, model, name = None):
        """Initializes a new sub-model."""
        self._main_model = model.get_main_model()
        self._model = model
        self._name = name
        self._var_prefix = '_sub_' + str(SubModel._next_id)
        SubModel._next_id += 1
        if (name is None) or model.is_source_prefix_mangled():
            self._source_prefix_mangled = True
            self._source_prefix = self._var_prefix
        else:
            self._source_prefix_mangled = False
            self._source_prefix = model.get_source_prefix() + name + '.'

    def get_main_model(self):
        """Return the main model."""
        return self._main_model

    def get_parent_model(self):
        """Return the parent model."""
        return self._model

    def get_base_comp(self):
        """Get the basic computation type."""
        return self._main_model.get_base_comp()

    def get_var_prefix(self):
        """Return the variable prefix."""
        return self._var_prefix

    def is_source_prefix_mangled(self):
        """Whether the source name prefix is mangled."""
        return self._source_prefix_mangled

    def get_source_prefix(self):
        """Return the source name prefix."""
        return self._source_prefix

    def add_pragma(self, pragma):
        """Add the specified pragma."""
        self._main_model.add_pragma(pragma)

    def add_package_import(self, package):
        """Add the specified package to import."""
        self._main_model.add_package_import(package)

    def add_package_location(self, package_location):
        """Add the specified package location."""
        self._main_model.add_package_location(package_location)

    def add_extra_dep(self, extra_dep):
        """Add the specified extra dependency."""
        self._main_model.add_extra_dep(extra_dep)

    def add_module_import(self, module):
        """Add the specified module to import."""
        self._main_model.add_module_import(module)

    def add_var(self, name, comp):
        """Add a new variable with the specified definition."""
        self._main_model.add_var(name, comp)

    def add_lazy_var(self, name):
        """Add a new variable that will be defined lazily."""
        self._main_model.add_lazy_var(name)

    def add_action(self, action):
        """Add the specified action."""
        self._main_model.add_action(action)

    def add_port(self, port):
        """Add the specified port for completeness test."""
        self._main_model.add_port(port)

    def add_result_source(self, source):
        """Add the specified result source."""
        self._main_model.add_result_source(source)

    def add_transact_type(self, transact_type):
        """Add the specified transact type."""
        self._main_model.add_transact_type(transact_type)
