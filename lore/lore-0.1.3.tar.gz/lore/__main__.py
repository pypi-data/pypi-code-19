import argparse
import atexit
import glob
import os
import sys
import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict
import re
import shutil
import subprocess
import logging

import lore
from lore import ansi, env, util
from lore.util import timer, which


logger = logging.getLogger(__name__)


class HelpfulParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help(sys.stderr)
        self.exit(2, ('%s: error: %s\n') % (self.prog, message))

    
def main(args=None):
    parser = HelpfulParser(prog='lore')
    parser.add_argument('--version', action='version',
                        version='lore %s' % lore.__version__)

    commands = parser.add_subparsers( help='common commands')
    
    init_parser = commands.add_parser('init', help='create a new lore project')
    init_parser.set_defaults(func=init)
    init_parser.add_argument('NAME', help='the name of the project')
    init_parser.add_argument('--git-ignore', default=True)
    init_parser.add_argument('--python-version', default=None)

    api_parser = commands.add_parser(
        'api',
        help='serve the api'
    )
    api_parser.set_defaults(func=api)

    console_parser = commands.add_parser(
        'console',
        help='launch an interactive python shell'
    )
    console_parser.set_defaults(func=console)

    exec_parser = commands.add_parser(
        'exec',
        help='run a shell command in this project\'s virtual env'
    )
    exec_parser.set_defaults(func=execute)

    install_parser = commands.add_parser(
        'install',
        help='install dependencies in a virtualenv'
    )
    install_parser.set_defaults(func=install)
    install_parser.add_argument(
        '--native',
        help='build optimized native dependencies (tensorflow)',
        action='store_true'
    )
    install_parser.add_argument(
        '--upgrade',
        help='recalculate requirements.frozen.txt with current versions',
        action='store_true'
    )

    task_parser = commands.add_parser(
        'task',
        help='run a task from the command line'
    )
    task_parser.set_defaults(func=task)

    pip_parser = commands.add_parser(
        'pip',
        help='pass a command to this project\'s virtual env pip'
    )
    pip_parser.set_defaults(func=pip)

    python_parser = commands.add_parser(
        'python',
        help='pass a command to this project\'s virtual env python'
    )
    python_parser.set_defaults(func=python)

    test_parser = commands.add_parser(
        'test',
        help='run tests'
    )
    test_parser.set_defaults(func=test)

    (known, unknown) = parser.parse_known_args(args)
    known.func(known, unknown)
    

def validate():
    if not env.exists():
        sys.exit(
            ansi.error() + ' %s is only available in lore '
                           'project directories (missing %s)' % (
                ansi.bold(sys.argv[1]),
                ansi.underline(env.version_path)
            )
        )


def api(parsed, unknown):
    validate()
    launch_virtual_env()
    check_requirements()
    
    from hub.listeners.endpoint import EndpointListener
    
    for path in glob.glob(os.path.join(env.root, 'app', 'api', '*_endpoint.py')):
        module = os.path.basename(path)[:-3]
        if sys.version_info.major == 2:
            import imp
            imp.load_source(module, path)
        elif sys.version_info.major == 3:
            import importlib.util
            spec = importlib.util.spec_from_file_location(module, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
    util.strip_one_off_handlers()
    
    EndpointListener(
        env.project,
        host_index=os.environ.get("RABBIT_HOST_INDEX"),
        concurrency=4
    ).start()


def console(parsed, unknown):
    validate()
    launch_virtual_env()
    check_requirements()
    
    import readline
    history = os.path.join(env.prefix, 'history')
    readline.parse_and_bind('tab: complete')
    if os.path.exists(history):
        readline.read_history_file(history)
    
    import atexit
    atexit.register(lambda: readline.write_history_file(history))
    
    vars = globals().copy()
    vars.update(locals())
    
    import code
    import socket
    import getpass
    shell = code.InteractiveConsole(vars)
    env_color = {
        env.DEVELOPMENT: ansi.GREEN,
        env.TEST: ansi.BLUE,
        env.PRODUCTION: ansi.RED
    }[env.name]
    
    sys.ps1 = ansi.foreground(env_color, '>>>')
    sys.ps2 = ansi.foreground(env_color, '...')
    
    banner = '%s in %s %s (Python %s)' % (
        ansi.foreground(ansi.GREEN, env.project.capitalize()),
        ansi.foreground(env_color, env.name),
        ansi.foreground(ansi.CYAN,
                        getpass.getuser() + '@' + socket.gethostname()),
        env.python_version
    )
    
    shell.interact(banner)

    
def execute(parsed, unknown):
    validate()
    launch_virtual_env()
    check_requirements()
    
    if len(unknown) == 0:
        print(ansi.error() + ' no args to execute!')
        return
    
    print(ansi.success('EXECUTE ') + ' '.join(unknown))
    
    os.environ['PATH'] = os.path.join(env.prefix, 'bin') + ':' + os.environ['PATH']
    subprocess.check_call(env.args, env=os.environ)


def init(parsed, unknown):
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


def install(parsed, unknown):
    validate()
    launch_virtual_env()
    install_requirements(parsed)
    
    if parsed.native:
        install_tensorflow()


def task(parsed, unknown):
    task = unknown[0]
    try:
        import app.tasks
    except:
        pass
    print(ansi.success())
    
    
def pip(parsed, unknown):
    validate()
    launch_virtual_env()
    check_requirements()
    
    args = [env.bin_pip] + unknown
    print(ansi.success('EXECUTE ') + ' '.join(args))
    subprocess.check_call(args)


def python(parsed, unknown):
    validate()
    launch_virtual_env()
    check_requirements()
    
    args = [env.bin_python] + unknown
    print(ansi.success('EXECUTE ') + ' '.join(args))
    subprocess.check_call(args)


def test(parsed, unknown):
    with timer('boot time'):
        validate()
        launch_virtual_env()
        check_requirements()
        
        if 'LORE_ENV' not in os.environ:
            env.name = env.TEST
            logger.level = logging.WARN
        
        import unittest
        suite = unittest.defaultTestLoader.discover(env.tests_dir)
    unittest.TextTestRunner().run(suite)


def install_homebrew():
    if not which('brew'):
        sys.exit(ansi.error() + ' you need to install homebrew first.')


def install_bazel():
    if not which('bazel'):
        sys.exit(
            ansi.error() + ' you need to install bazel. On OS X run:\n'
                           ' $ brew install bazel'
        )


def install_tensorflow():
    description = subprocess.check_output(
        (env.bin_pip, 'show', 'tensorflow')
    ).decode('utf-8')
    version = re.match(
        '.*^Version: ([^\n]+)', description, re.S | re.M
    ).group(1)
    if not version:
        sys.exit(ansi.error() + ' tensorflow is not in requirements.txt')
    
    print(ansi.success('NATIVE') + ' tensorflow ' + version)

    cached = os.path.join(
        env.pyenv,
        'cache',
        'tensorflow_pkg',
        'tensorflow-' + version + '*'
    )
    
    paths = glob.glob(cached)
    
    if not paths:
        build_tensorflow(version)
        paths = glob.glob(cached)

    path = paths[0]
    
    subprocess.check_call((env.bin_pip, 'uninstall', '-y', 'tensorflow'))
    subprocess.check_call((env.bin_pip, 'install', path))


def build_tensorflow(version):
    install_bazel()
    print(ansi.success('BUILD') + ' tensorflow for this architecture')
    
    tensorflow_repo = os.path.join(env.pyenv, 'cache', 'tensorflow')
    cache = os.path.join(env.pyenv, 'cache', 'tensorflow_pkg')
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
    major, minor, patch = env.python_version.split('.')
    lib = os.path.join('lib', 'python' + major + '.' + minor, 'site-packages')
    new_env = {
        'PATH': os.environ['PATH'],
        'PYTHON_BIN_PATH': env.bin_python,
        'PYTHON_LIB_PATH': os.path.join(env.prefix, lib),
        'TF_NEED_MKL': '0',
        'CC_OPT_FLAGS': '-march=native -O2',
        'TF_NEED_JEMALLOC': '1',  # only available on linux regardless
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
    subprocess.check_call(('./configure',), cwd=tensorflow_repo, env=new_env)
    subprocess.check_call(('./configure',), cwd=tensorflow_repo, env=new_env)
    
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


def install_python_version():
    if not env.python_version:
        env.set_python_version('.'.join(sys.version_info))
        print(ansi.warning() + ' %s does not exist. Creating with %s' %
              (env.version_path, env.python_version))
        with open(env.version_path, 'w') as f:
            f.write(env.python_version + '\n')
    
    if not env.pyenv:
        sys.exit(
            ansi.error() + ' pyenv is not installed. Lore is broken. try:\n'
            ' $ lore pip uninstall lore && lore pip install lore\n'
        )
    
    versions = subprocess.check_output(
        (env.bin_pyenv, 'versions', '--bare')
    ).decode('utf-8').split('\n')
    if env.python_version not in versions:
        print(
            ansi.warning() + ' python %s is not installed. Installing with '
                             'pyenv.' % env.python_version
        )
        print(ansi.success('CHECK ') + 'xcode-select --install')
        subprocess.call(('xcode-select', '--install'),
                        stderr=subprocess.PIPE)
        subprocess.check_call((env.bin_pyenv, 'install', env.python_version))
        subprocess.check_call((env.bin_pyenv, 'rehash'))
        pip = os.path.join(
            env.pyenv,
            'versions',
            env.python_version,
            'bin',
            'pip'
        )
        subprocess.check_call((pip, 'install', 'lore'))


def launch_virtual_env():
    install_python_version()
    
    if sys.prefix == env.prefix:
        try:
            import keras
            def cleanup_tensorflow():
                # Not strictly necessary, but prevents random gc exception at exit
                keras.backend.clear_session()
        
            atexit.register(cleanup_tensorflow)
        except:
            pass
        
        return
    
    if not os.path.exists(env.prefix):
        print(ansi.success('CREATE') + ' virtualenv: %s' % env.project)
        try:
            shutil.rmtree(os.path.join(env.pyenv, 'versions', env.project))
        except OSError as e:
            if e.errno != os.errno.ENOENT:
                raise
        
        subprocess.check_call((
            env.bin_pyenv,
            'virtualenv',
            env.python_version,
            env.project
        ))
        # TODO gather lore version from requirements.frozen.txt first
        subprocess.check_call((env.bin_pip, 'install', 'lore'))
    os.execv(env.bin_lore, sys.argv)


def install_requirements(args):
    # Find requirements source
    source = 'requirements.frozen.txt'
    if not os.path.exists(source) or args.upgrade:
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
    
    clean_vcs_lines(source)
    pip_install(source, args)
    pip_install('requirements.vcs.txt', args)
    freeze_requirements()
    subprocess.check_call((
        env.bin_python,
        '-m',
        'ipykernel',
        'install',
        '--user',
        '--name=' + env.project
    ))


def freeze_requirements():
    destination = 'requirements.frozen.txt'
    source = 'requirements.txt'
    freeze = subprocess.Popen(
        (env.bin_pip, 'freeze', '-r', source),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    (frozen, missing) = freeze.communicate()
    freeze.wait()
    
    frozen = frozen.decode('utf-8').split('\n')
    missing = missing.decode('utf-8').split('\n')
    new = [line for line in missing if 'package is not installed' in line]
    regex = re.compile(r'contains ([\w\-\_]+)')
    packages = [m.group(1) for l in new for m in [regex.search(l)] if m]
    
    if packages:
        args = [env.bin_pip, 'install'] + packages
        print(ansi.success('EXECUTE ') + ' '.join(args))
        subprocess.check_call(args)
        return freeze_requirements()
    
    extras = frozen.index(
        '## The following requirements were added by pip freeze:'
    )
    if extras:
        frozen = frozen[:extras]
    with open(destination, 'w') as f:
        f.write('\n'.join(frozen).strip() + '\n')
    clean_vcs_lines(destination)


def clean_vcs_lines(requirements):
    with open(requirements, 'r') as f:
        lines = f.readlines()
    
    vcs = [line for line in lines if
           re.match(r'^(-e )?(git|svn|hg|bzr).*', line)]
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


def pip_install(path, args):
    if not os.path.exists(path):
        return
    
    pip_args = [env.bin_pip, 'install', '-r', path]
    if args.upgrade:
        pip_args += ['--upgrade']
        pip_args += ['--upgrade-strategy=eager']
    print(ansi.success('EXECUTE ') + ' '.join(pip_args))
    try:
        subprocess.check_call(pip_args)
    except subprocess.CalledProcessError:
        sys.exit(
            ansi.error() + ' could not:\n $ lore pip install -r %s\nPlease try '
                           'installing failed packages manually, or upgrade failed '
                           'packages by removing ' % path +
            ansi.underline('requirements.frozen.txt') +
            '\n $ rm requirements.frozen.txt'
        )


def check_requirements():
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
    except (pkg_resources.ContextualVersionConflict, DistributionNotFound,
            VersionConflict) as error:
        sys.exit(
            ansi.error() + ' missing requirement:\n  ' + str(
                error) +
            '\nPlease run:\n $ lore install\n'
        )
    

if __name__ == '__main__':
    try:
        main()
    except:
        e = sys.exc_info()
        for i in e:
            print(i)
        import traceback
        traceback.print_tb(e[2])


