
SETUP_INFO = dict(
    name = 'infi.traceback',
    version = '0.3.15',
    author = 'Arnon Yaari',
    author_email = 'arnony@infinidat.com',

    url = 'https://github.com/Infinidat/infi.traceback',
    license = 'BSD',
    description = """better tracebacks""",
    long_description = """Tracebacks in Python are missing some useful debugging information, such is locals() in each stack frame
This module provides several mechanisms for better tracebacks:
* traceback_context. A context that in patches standard's library traceback module to print better tracebacks
* traceback_decorator. A decorator that calls the decorated method inside the traceback_context
* Nose Plugin. The plugin, enabled with '--with-infi-traceback', prints a better traceback for errors and failures
* pretty_traceback_and_exit_decorator. A decorator for console script entry points that prints exceptions and raises SystemExit""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = [
'infi.exceptools',
'infi.pyutils',
'nose',
'setuptools'
],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = [],
        gui_scripts = [],
        ),
)

if SETUP_INFO['url'] is None:
    _ = SETUP_INFO.pop('url')

SETUP_INFO['entry_points']['nose.plugins'] = ['infi.traceback = infi.traceback:NosePlugin']

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

