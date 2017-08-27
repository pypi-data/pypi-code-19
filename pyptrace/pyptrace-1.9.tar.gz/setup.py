from setuptools import setup, find_packages, Extension

extos_module = Extension('pyptrace.ext.os._os',
    define_macros = [('MAJOR_VERSION', '1'), ('MINOR_VERSION', '9')],
    sources=['pyptrace/ext/os/os.c'])

setup(
    name = 'pyptrace',
    description = 'Python wrapper for Linux ptrace system call.',
    author = 'wenlin.wu',
    author_email = 'wenlin.wu@outlook.com',
    url = 'https://github.com/kikimo/pyptrace',
    version = '1.9',
    packages = find_packages(),
    package_dir = {'':'.'},
    ext_modules = [extos_module],
    keywords = 'linux ptrace',
)
