import os
import sys
import ansi
import util
import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict
import re
import subprocess
import glob



# Environment Variables
# ----------------------------------
for var in glob.glob("/conf/env/*"):
    if os.path.isfile(var):
        os.environ[os.path.basename(var)] = open(var).read()

env_file = '.env'
if os.path.isfile(env_file):
    from dotenv import load_dotenv
    load_dotenv(env_file)


class App(object):
    def __init__(self):
        self.env = os.environ.get('LORE_ENV', 'development')
        self.project = os.getcwd().split(os.sep)[-1]
        self.root = os.getcwd()
        sys.path = [self.root] + sys.path

        if self.env == 'test':
            self.work_dir = 'tests'
        elif 'DOMINO_WORKING_DIR' in os.environ:
            self.work_dir = os.environ.get('DOMINO_WORKING_DIR')
        else:
            self.work_dir = self.root

        self.models_dir = os.path.join(self.work_dir, 'models')
        self.data_dir = os.path.join(self.work_dir, 'data')
        self.tests_dir = os.path.join(self.root, 'tests')
        self.version_path = '.python-version'
        self.pyenv = os.path.join(os.environ['HOME'], '.pyenv')
        self._python_version = None
        self.prefix = None
        self.python = None
        self.pip = None
        self.lore = None
        
        if os.path.exists(self.version_path):
            with open(self.version_path, 'r') as f:
                self.python_version = f.read().strip()
        else:
            self.python_version = None
    
    @property
    def python_version(self):
        return self._python_version
    
    @python_version.setter
    def python_version(self, python_version):
        self._python_version = python_version
        if self.python_version:
            self.prefix = os.path.join(
                os.environ['HOME'],
                '.pyenv',
                'versions',
                self.python_version,
                'envs',
                self.project
            )
            self.python = os.path.join(self.prefix, 'bin', 'python')
            self.pip = os.path.join(self.prefix, 'bin', 'pip')
            self.lore = os.path.join(self.prefix, 'bin', 'lore')
        else:
            self.python = None
            self.pip = None
            self.lore = None
    
    def exists(self):
        return self.python_version
    
    def validate(self):
        if not self.exists():
            sys.exit(
                ansi.error() + ' %s is only available in lore '
                               'project directories (missing %s)' % (
                    ansi.bold(sys.argv[1]),
                    ansi.underline(self.version_path)
                )
            )
    
    def install(self, args):
        self.validate()
        self.launch_virtual_env()
        self.install_requirements()
        
        if args.native:
            self.install_tensorflow()

    def install_homebrew(self):
        if not util.which('brew'):
            sys.exit(ansi.error + ' you need to install homebrew first.')

    def install_bazel(self):
        if not util.which('bazel'):
            sys.exit(ansi.error + ' you need to install bazel. On OS X run:\n '
                                  '$ brew install bazel')
        
    def install_tensorflow(self):
        description = subprocess.check_output((self.pip, 'show', 'tensorflow'))
        version = re.match('.*^Version: ([^\n]+)', description, re.S | re.M).group(1)
        if not version:
            sys.exit(ansi.error() + ' tensorflow is not in requirements.txt')

        print(ansi.success('NATIVE') + ' tensorflow ' + version)

        path = glob.glob(os.path.join(
            self.pyenv,
            'cache',
            'tensorflow_pkg',
            'tensorflow-' + version + '*'
        ))

        if path:
            path = path[0]
        else:
            self.build_tensorflow()
            
        subprocess.check_call((self.pip, 'uninstall', '-y', 'tensorflow'))
        subprocess.check_call((self.pip, 'install', path))

    def build_tensorflow(self):
        self.install_bazel()
        print(ansi.success('BUILD') + ' tensorflow for this architecture')
    
        tensorflow_repo = os.path.join(self.pyenv, 'cache', 'tensorflow')
        cache = os.path.join(self.pyenv, 'cache', 'tensorflow_pkg')
        if not os.path.exists(tensorflow_repo):
            subprocess.check_call((
                'git',
                'clone',
                'https://github.com/tensorflow/tensorflow',
                tensorflow_repo
            ))
    
        subprocess.check_call(
            ('git', 'checkout', '--', '.'),
            cwd=tensorflow_repo
        )
        subprocess.check_call(
            ('git', 'checkout', 'master'),
            cwd=tensorflow_repo
        )
        subprocess.check_call(
            ('git', 'pull'),
            cwd=tensorflow_repo
        )
        subprocess.check_call(
            ('git', 'checkout', 'v' + version),
            cwd=tensorflow_repo
        )
        env = {
            'PATH': os.environ['PATH'],
            'PYTHON_BIN_PATH': self.python,
            'PYTHON_LIB_PATH': os.path.join(self.prefix, 'lib', 'python2.7',
                                            'site-packages'),
            'TF_NEED_MKL': '0',
            'CC_OPT_FLAGS': '-march=native -O2',
            'TF_NEED_JEMALLOC': '0',  # TODO enable on linux only
            'TF_NEED_GCP': '0',
            'TF_NEED_HDFS': '0',
            'TF_ENABLE_XLA': '0',
            'TF_NEED_VERBS': '0',
            'TF_NEED_OPENCL': '0',
            'TF_NEED_CUDA': '0',  # TODO enable CUDA when appropriate
            'TF_CUDA_CLANG': '1',
            'TF_CUDA_VERSION': '8.0.61',
            'CUDA_TOOLKIT_PATH': '/usr/local/cuda',
            'CUDNN_INSTALL_PATH': '/usr/local/cuda',
            'TF_CUDNN_VERSION': '5.1.10',
            'TF_CUDA_CLANG': '/usr/bin/gcc',
            'TF_CUDA_COMPUTE_CAPABILITIES': '3.5,5.2',
        }
        subprocess.check_call(('./configure',), cwd=tensorflow_repo, env=env)
        subprocess.check_call(('./configure',), cwd=tensorflow_repo, env=env)
    
        subprocess.check_call((
            'bazel',
            'build',
            '--config=opt',
            # '--config=cuda',  TODO enable CUDA when appropriate
            'tensorflow/tools/pip_package:build_pip_package',
        ), cwd=tensorflow_repo)
    
        subprocess.check_call((
            'bazel-bin/tensorflow/tools/pip_package/build_pip_package',
            cache
        ), cwd=tensorflow_repo)

    def console(self):
        self.validate()
        self.launch_virtual_env()
        self.check_requirements()
        
        import readline
        import code
        import atexit
        import socket
        import getpass
        if sys.version_info.major == 2 and sys.version_info.minor == 7:
            history = os.path.join(self.prefix, 'history')
            readline.parse_and_bind('tab: complete')
            
            def save_history(path=history):
                readline.write_history_file(path)
            
            if os.path.exists(history):
                readline.read_history_file(history)
            
            atexit.register(save_history)
        
        vars = globals().copy()
        vars.update(locals())
        shell = code.InteractiveConsole(vars)
        banner = '%s %s (Python %s)' % (
            ansi.foreground(ansi.GREEN, self.project.capitalize()),
            ansi.foreground(ansi.CYAN,
                            getpass.getuser() + '@' + socket.gethostname()),
            self.python_version
        )
        if 'LORE_ENV' not in os.environ:
            os.environ['LORE_ENV'] = 'developement'
        shell.interact(banner)
    
    def test(self):
        import unittest
        
        self.validate()
        self.launch_virtual_env({'LORE_ENV': 'test'})
        self.check_requirements()
        
        suite = unittest.defaultTestLoader.discover(self.tests_dir)
        unittest.TextTestRunner().run(suite)
    
    def install_python_version(self):
        if not self.python_version:
            self.python_version = '.'.join(sys.version_info)
            print(ansi.warning() + ' %s does not exist. Creating with %s' %
                  (self.version_path, self.python_version))
            with open(self.version_path, 'w') as f:
                f.write(self.python_version + '\n')
        
        pyenv = util.which('pyenv')
        if not pyenv:
            sys.exit(
                ansi.error() + ' pyenv is not installed. Lore is broken. '
                               'try:\n $ pip uninstall lore && pip install lore\n'
            )
        
        versions = subprocess.check_output(
            ('pyenv', 'versions', '--bare')
        ).split('\n')
        if self.python_version not in versions:
            print(
                ansi.warning() + ' python %s is not installed. Installing with '
                                 'pyenv.' % self.python_version
            )
            subprocess.check_call(('pyenv', 'install', self.python_version))
            subprocess.check_call(('pyenv', 'rehash'))
            pip = os.path.join(pyenv, 'versions', self.python_version, 'bin',
                               'pip')
            subprocess.check_call((pip, 'install', 'lore'))
    
    def launch_virtual_env(self, env={}):
        self.install_python_version()
        new_env = os.environ.copy()
        new_env.update(env)
    
        if sys.prefix == self.prefix:
            return

        if not os.path.exists(self.prefix):
            print(ansi.success('CREATE') + ' virtualenv: %s' % self.project)
            try:
                os.remove(os.path.join(self.pyenv, 'versions', self.project))
            except OSError as e:
                if e.errno != os.errno.ENOENT:
                    raise

            subprocess.check_call((
                'pyenv',
                'virtualenv',
                self.python_version,
                self.project
            ))
            # TODO gather lore version from requirements.frozen.txt first
            subprocess.check_call((self.pip, 'install', 'lore'))
        
        os.execve(self.lore, sys.argv, new_env)
    
    def install_requirements(self):
        # Find requirements source
        source = 'requirements.frozen.txt'
        if not os.path.exists(source):
            print(
                ansi.warning() + ' %s is missing. You should add it to version '
                                 'control.' % ansi.underline(source)
            )
            source = 'requirements.txt'
        
        if not os.path.exists(source):
            sys.exit(
                ansi.error() + ' %s is missing. Please create it.' %
                (ansi.underline(source))
            )
        
        self.clean_vcs_lines(source)
        self.pip_install(source)
        self.pip_install('requirements.vcs.txt')
        self.freeze_requirements()
    
    def freeze_requirements(self):
        destination = 'requirements.frozen.txt'
        source = 'requirements.txt'
        freeze = subprocess.Popen(
            (self.pip, 'freeze', '-r', source),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        (frozen, missing) = freeze.communicate()
        freeze.wait()
        
        frozen = frozen.split('\n')
        missing = missing.split('\n')
        new = [line for line in missing if 'package is not installed' in line]
        regex = re.compile(r'contains ([\w\-\_]+)')
        packages = [m.group(1) for l in new for m in [regex.search(l)] if m]
        
        if packages:
            args = [self.pip, 'install'] + packages
            print(ansi.success('EXECUTE ') + ' '.join(args))
            subprocess.check_call(args)
            return self.freeze_requirements()
        
        extras = frozen.index(
            '## The following requirements were added by pip freeze:'
        )
        if extras:
            frozen = frozen[:extras]
        with open(destination, 'w') as f:
            f.write('\n'.join(frozen).strip() + '\n')
        self.clean_vcs_lines(destination)
        
    def clean_vcs_lines(self, requirements):
        with open(requirements, 'r') as f:
            lines = f.readlines()
        
        vcs = [line for line in lines if re.match(r'^(-e )?(git|svn|hg|bzr).*', line)]
        if not vcs:
            return
        
        vcs_file = 'requirements.vcs.txt'
        print(
            ansi.warning() + ' moving version controlled requirements to %s'
                             '\n  %s' % (
            ansi.underline(vcs_file), '  '.join(vcs))
        )
        if os.path.exists(vcs_file):
            with open(vcs_file, 'r') as f:
                vcs = list(set(vcs).union(set(f.readlines())))
        
        lines = list(set(lines) - set(vcs))
        with open(requirements, 'w') as f:
            f.write(''.join(sorted(lines)))
        
        with open(vcs_file, 'w') as f:
            f.write(''.join(sorted(vcs)))
    
    def pip_install(self, path):
        if not os.path.exists(path):
            return
        
        args = (self.pip, 'install', '-r', path)
        print(ansi.success('EXECUTE ') + ' '.join(args))
        try:
            subprocess.check_call(args)
        except subprocess.CalledProcessError:
            sys.exit(
                ansi.error() + ' could not:\n $ pip install -r %s\nPlease try '
                               'installing failed packages manually.' % path
            )
    
    def check_requirements(self):
        path = 'requirements.frozen.txt'
        if not os.path.exists(path):
            sys.exit(
                ansi.error() + ' %s is missing. Please run:\n '
                               '$ lore install\n' % ansi.underline(path)
            )
        
        with open(path, 'r') as f:
            dependencies = f.readlines()
        
        try:
            pkg_resources.require(dependencies)
        except (DistributionNotFound, VersionConflict) as error:
            sys.exit(
                ansi.error() + ' missing requirement:\n  ' + str(
                    error) +
                '\nPlease run:\n $ lore install\n'
            )

    def pip_exec(self, args):
        self.validate()
        self.launch_virtual_env()
        self.check_requirements()

        args = [self.pip] + args
        print(ansi.success('EXECUTE ') + ' '.join(args))
        subprocess.check_call(args)

    def python_exec(self, args):
        self.validate()
        self.launch_virtual_env()
        self.check_requirements()

        args = [self.python] + args
        print(ansi.success('EXECUTE ') + ' '.join(args))
        subprocess.check_call(args)

    def initialize(self):
        raise "Not Implemented"
        # check_python_version(args.python_version)
        # root = mkdir(args.NAME)
        # install_template('README.rst', root)
        # install_template('requirements.txt', root)
        # install_template('.gitignore', root)
        # install_template('.python-version', root, version=version)
        #
        # config = mkdir(os.path.join(args.NAME, 'config'))
        #
        # src = mkdir(os.path.join(args.NAME, 'src'))
        # install_template('__init__.py', src)
        #
        # tests = mkdir(os.path.join(args.NAME, 'tests'))
        #
        # run('pip install -r requirements.txt')
        #
        # # create directory structure
        # # create requirements.txt/readme/configuration files
        # # create pyenv
        # # virtualenv


# TODO add this kernel to jupyter
# TODO pip install jupyter ipykernel
# TODO  ~/.pyenv/versions/picking/bin/python -m ipykernel install --user --name=Picking

