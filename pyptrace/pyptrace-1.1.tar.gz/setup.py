from setuptools import setup, find_packages, Extension

ptrace_module = Extension('ptrace_wrapper',
    define_macros = [('MAJOR_VERSION', '2'),
        ('MINOR_VERSION', '1')],
    include_dirs = ['/usr/local/include'],
    # libraries = ['pthread'],
    library_dirs = ['/usr/local/lib'],
    sources=['libptrace/ptrace.c'])

setup(
    name = 'pyptrace',
    description = 'python wrapper for ptrace',
    author = 'wenlin.wu',
    author_email = 'wenlin.wu@outlook.com',
    url = 'https://github.com/kikimo/pyptrace',
    version = '1.1',
    packages = find_packages('src'),
    package_dir = {'':'src'},
    ext_modules = [ptrace_module]
)
