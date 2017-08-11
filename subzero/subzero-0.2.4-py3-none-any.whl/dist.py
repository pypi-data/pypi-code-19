import distutils.command.build
import distutils.version
import json
import ntpath
import os
import pkgutil
import pkg_resources
import shutil
import subprocess
import sys
import PyInstaller.__main__
import logging

from subprocess import CalledProcessError
from pip.commands.show import search_packages_info
from PyInstaller.building.makespec import main as makespec_main
from PyInstaller.utils.hooks import collect_submodules, get_module_file_attribute
from packaging import version
from pkg_resources import EntryPoint, Requirement
from pyspin.spin import make_spin, Spin1
from copy import copy

from .utils import suppress, makespec_args, decode, is_binary, rename_script, build_dir, entry_keys, move_tree

logger = logging.getLogger('PyInstaller')

class build_exe(distutils.core.Command):
    description = "build executables from Python scripts"
    user_options = []
    boolean_options = []

    def initialize_options(self):
        distutils.command.build.build.initialize_options(self)
        self.build_exe = None
        self.optimize_imports = True
        self.executables = []
        self._script_names = []

        for name in makespec_args():
            if not getattr(self, name, None):
                setattr(self, name, None)

    def finalize_options(self):
        distutils.command.build.build.finalize_options(self)
        if self.build_exe is None:
            self.build_exe = os.path.join(self.build_base, build_dir())

    def run(self):
        entry_points = {}
        gui_scripts = []

        entry_points_map = EntryPoint.parse_map(self.distribution.entry_points)
        for entry_key in entry_keys:
            with suppress(KeyError):
                entry_points.update(entry_points_map[entry_key])
                if entry_key == 'gui_scripts':
                    gui_scripts.extend(entry_points_map[entry_key].keys())

        try:
            options = {}
            for key, value in dict(
                    self.distribution.command_options['build_exe']).items():
                options[key] = value[1]
        except (KeyError, TypeError):
            options = {}

        scripts = copy(self.distribution.scripts)
        self.distribution.scripts = []

        workpath = os.path.join(self.build_temp, 'workpath')
        distpath = os.path.join(self.build_temp, 'distpath')

        for required_directory in [distpath, self.build_exe, workpath]:
            shutil.rmtree(required_directory, ignore_errors=True)
            os.makedirs(required_directory, exist_ok=True)

        for entry_point in entry_points.values():
            scripts.append(self._generate_script(entry_point, workpath))

        lib_dirs = ['lib', 'lib{}'.format(build_dir()[3:])]
        for lib_dir in lib_dirs:
            shutil.rmtree(
                os.path.join(self.build_base, lib_dir), ignore_errors=True)

        self.run_command('build')

        for default_option in ['pathex', 'hiddenimports', 'binaries']:
            options.setdefault(default_option, [])

        # by convention, all paths appended to py_options must be absolute
        for lib_dir in lib_dirs:
            if os.path.isdir(os.path.join(self.build_base, lib_dir)):
                options['pathex'].append(
                    os.path.abspath(os.path.join(self.build_base, lib_dir)))

        if not options['pathex']:
            raise ValueError('Unable to find lib directory!')

        options['specpath'] = os.path.abspath(workpath)
        options['pathex'].append(os.path.abspath(workpath))

        for i, tp in enumerate(options.setdefault('datas', [])):
            options['datas'][i] = (os.path.abspath(options['datas'][i][0]),
                                   options['datas'][i][1])

        if not self.optimize_imports:
            self._discover_dependencies(options)

        executables = []
        for script, executable in zip(scripts, self.executables):
            executable = executable or Executable(script)
            executable.script = script
            executable._options = dict(options, **executable.options)
            executable._options['name'] = '.'.join(
                ntpath.basename(script).split('.')[:-1])
            if executable._options['name'] in gui_scripts:
                executable._options['console'] = False

            executables.append(executable)

        for executable in executables:
            rename_script(executable)

        for executable in executables:
            self._freeze(executable, workpath, distpath)

        # TODO: Compare file hashes to make sure we haven't replaced files with
        # a different version
        names = [executable.options['name'] for executable in executables]
        for name in names[1:]:
            move_tree(
                os.path.join(distpath, name), os.path.join(distpath, names[0]))

        move_tree(os.path.join(distpath, names[0]), self.build_exe)

        shutil.rmtree(self.build_temp, ignore_errors=True)
        shutil.rmtree(distpath, ignore_errors=True)

    @make_spin(Spin1, 'Compiling module file locations...')
    def _compile_modules(self):
        modules = {}

        for module_finder, name, ispkg in pkgutil.walk_packages():
            for attempt in range(2):
                with suppress((AttributeError, ImportError)):
                    if attempt == 0:
                        loader = module_finder.find_spec(name).loader
                        filename = loader.get_filename(name)
                    elif attempt == 1:
                        filename = get_module_file_attribute(name)
                    break
            else:
                continue

            modules[os.path.abspath(filename)] = name

        return modules

    @make_spin(Spin1, 'Compiling project requirements...')
    def _compile_requirements(self):
        packages = set()
        for requirement in self.distribution.install_requires:
            requirement = Requirement.parse(requirement)
            packages.add(requirement.key)

        # Create the dependency map
        entries = json.loads(
            decode(subprocess.check_output(['pipdeptree', '--json'])))
        entry_map = { entry['package']['key'] : 
                        set([ dependency['key'] for dependency in entry['dependencies'] ]) for entry in entries }

        while True:
            for package in packages:
                if package in entry_map and not entry_map[package] < packages:
                    packages.update(entry_map[package])
                    break
            else:
                break

        module_files = set()
        binary_files = set()

        for package in packages:
            in_header = True
            root = None
            
            for info in search_packages_info(package):
                files = info['files']
                root = info['location']
                for file in files:
                    full_path = os.path.abspath(
                        os.path.join(root, file))
                    if full_path.endswith('.py') or full_path.endswith('.pyc'):
                        module_files.add(full_path)
                    if is_binary(full_path):
                        binary_files.add(full_path)

        return module_files, binary_files

    def _discover_dependencies(self, options):
        # Requirements cannot be assumed to be modules / packages
        # options['hiddenimports'].extend(self.distribution.install_requires)

        if version.parse(sys.version[0:3]) >= version.parse('3.4'):
            for package in self.distribution.packages:
                options['hiddenimports'].extend(collect_submodules(package))

        module_files = self._compile_modules()
        required_module_files, required_binary_files = self._compile_requirements(
        )

        for required_file in required_module_files:
            try:
                options['hiddenimports'].append(module_files[required_file])
            except KeyError:
                logger.debug(
                    'Unable to collect module for {}'.format(required_file))

        for required_file in required_binary_files:
            # FIXME: Add to binaries rather than simply appending to pathex.
            options['pathex'].append(os.path.dirname(required_file))

        options['pathex'] = list(set(options['pathex']))

    def _generate_script(self, entry_point, workpath):
        """
        Generates a script given an entry point.
        """

        # note that build_scripts appears to work sporadically

        # entry_point.attrs is tuple containing function
        # entry_point.module_name is string representing module name
        # entry_point.name is string representing script name

        # script name must not be a valid module name to avoid name clashes on
        # import
        script_path = os.path.join(workpath, '{}.py'.format(entry_point.name))
        with open(script_path, 'w+') as fh:
            fh.write("import {0}\n".format(entry_point.module_name))
            fh.write("{0}.{1}()\n".format(entry_point.module_name, '.'.join(
                entry_point.attrs)))

            fh.seek(0)
            assert '==' not in fh.read()

        # Removed: requirements cannot be assumed to be packages
        #  + self.distribution.install_requires

        return script_path

    @staticmethod
    @make_spin(Spin1, 'Compiling executable...')
    def _freeze(executable, workpath, distpath):
        with suppress(OSError):
            os.remove(
                os.path.join(executable.options['specpath'], '{}.spec'.format(
                    executable.options['name'])))

        spec_file = PyInstaller.__main__.run_makespec([executable.script],
                                                      **executable.options)
        PyInstaller.__main__.run_build(
            None,
            spec_file,
            noconfirm=True,
            workpath=workpath,
            distpath=distpath)
        # os.remove(spec_file)


class Executable(object):
    def __str__(self):
        return self.script

    def __init__(self, script, **kwargs):
        self.script = script
        self._options = {}

        for name in kwargs:
            if name in makespec_args():
                self._options[name] = kwargs[name]

    @property
    def options(self):
        return self._options
