from setuptools import setup, find_packages, Extension

ptrace_module = Extension('_pyptrace',
    define_macros = [('MAJOR_VERSION', '1'), ('MINOR_VERSION', '8')],
    sources=['pyptrace/_pyptrace.c'])

extos_module = Extension('pyptrace.ext.os',
    define_macros = [('MAJOR_VERSION', '1'), ('MINOR_VERSION', '8')],
    sources=['pyptrace/ext/os.c'])

setup(
    name = 'pyptrace',
    description = 'Python wrapper for Linux ptrace system call.',
    author = 'wenlin.wu',
    author_email = 'wenlin.wu@outlook.com',
    url = 'https://github.com/kikimo/pyptrace',
    version = '1.8',
    packages = find_packages(),
    package_dir = {'':'.'},
    ext_modules = [ptrace_module, extos_module],
    keywords = 'linux ptrace',
)
