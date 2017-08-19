from setuptools import setup, find_packages, Extension

ptrace_module = Extension('_pyptrace',
    define_macros = [('MAJOR_VERSION', '1'),
        ('MINOR_VERSION', '6')],
    # include_dirs = ['/usr/local/include'],
    # libraries = ['pthread'],
    # library_dirs = ['/usr/local/lib'],
    sources=['pyptrace/_pyptrace.c'])

long_description = '''
--------------
Installation
--------------

-------
Usage
--------

-------
Links
-------
'''

setup(
    name = 'pyptrace',
    description = 'Python wrapper for Linux ptrace system call.',
    long_description = long_description,
    author = 'wenlin.wu',
    author_email = 'wenlin.wu@outlook.com',
    url = 'https://github.com/kikimo/pyptrace',
    version = '1.6',
    packages = find_packages(),
    package_dir = {'':'.'},
    ext_modules = [ptrace_module],
    package_data = {
        '': ['*.rst']
    }
)
