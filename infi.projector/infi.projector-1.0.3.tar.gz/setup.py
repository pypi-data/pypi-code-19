
SETUP_INFO = dict(
    name = 'infi.projector',
    version = '1.0.3',
    author = 'Arnon Yaari',
    author_email = 'arnony@infinidat.com',

    url = 'https://github.com/Infinidat/infi.projector',
    license = 'BSD',
    description = """Python project management tool""",
    long_description = """For the complete document, see the README.md file over at GitHub""",

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
'docopt',
'git-py',
'infi.execute',
'infi.recipe.python',
'infi.recipe.template.version',
'pip',
'setuptools',
'six',
'wheel',
'zc.buildout>=2.9.2'
],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': [
'.gitignore',
'buildout.cfg',
'get-pip.py',
'README.md',
'setup.in'
]},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = ['projector = infi.projector.scripts:projector'],
        gui_scripts = [],
        projector_command_plugins = ['repository = infi.projector.plugins.builtins.repository:RepositoryPlugin', 'envenv = infi.projector.plugins.builtins.devenv:DevEnvPlugin', 'version = infi.projector.plugins.builtins.version:VersionPlugin', 'requirements = infi.projector.plugins.builtins.requirements:RequirementsPlugin', 'console_scripts = infi.projector.plugins.builtins.console_scripts:ConsoleScriptsPlugin', 'gui_scripts = infi.projector.plugins.builtins.gui_scripts:GuiScriptsPlugin', 'package_scripts = infi.projector.plugins.builtins.package_scripts:PackageScriptsPlugin', 'package_data = infi.projector.plugins.builtins.package_data:PackageDataPlugin', 'isolated_pyton = infi.projector.plugins.builtins.isolated_python:IsolatedPythonPlugin', 'submodules = infi.projector.plugins.builtins.submodules:SubmodulePlugin']),
    )

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

