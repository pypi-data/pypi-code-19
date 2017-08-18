from setuptools import setup, find_packages, Extension

ptrace_module = Extension('_pyptrace',
    define_macros = [('MAJOR_VERSION', '1'),
        ('MINOR_VERSION', '2')],
    # include_dirs = ['/usr/local/include'],
    # libraries = ['pthread'],
    # library_dirs = ['/usr/local/lib'],
    sources=['pyptrace/_pyptrace.c'])

setup(
    name = 'pyptrace',
    description = 'python wrapper for ptrace',
    author = 'wenlin.wu',
    author_email = 'wenlin.wu@outlook.com',
    url = 'https://github.com/kikimo/pyptrace',
    version = '1.2',
    packages = find_packages(),
    package_dir = {'':'.'},
    ext_modules = [ptrace_module]
)
