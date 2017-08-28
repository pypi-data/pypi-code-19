import ast
import os.path

from setuptools import setup


def get_version():
    module_path = os.path.join(os.path.dirname(__file__), 'subtoml.py')
    module_file = open(module_path)
    try:
        module_code = module_file.read()
    finally:
        module_file.close()
    tree = ast.parse(module_code, module_path)
    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target, = node.targets
        if isinstance(target, ast.Name) and target.id == '__version__':
            value = node.value
            if isinstance(value, ast.Str):
                return value.s
            raise ValueError('__version__ is not defined as a string literal')
    raise ValueError('could not find __version__')


def readme():
    try:
        with open('README.rst') as f:
            return f.read()
    except IOError:
        pass


setup(
    name='subtoml',
    version=get_version(),
    description='Sed for TOML: subtitute parts of a TOML file',
    long_description=readme(),
    url='https://bitbucket.org/dahlia/subtoml',
    author='Hong Minhee',
    author_email='\x68\x6f\x6e\x67.minhee' '@' '\x67\x6d\x61\x69\x6c.com',
    license='GPLv3 or later',
    py_modules=['subtoml'],
    install_requires=['pytoml >= 0.1.12'],
    entry_points={
        'console_scripts': ['subtoml = subtoml:main']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: '
        'GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: Stackless',
        'Topic :: Software Development :: Pre-processors',
        'Topic :: Text Editors :: Text Processing',
        'Topic :: Text Processing :: Filters',
        'Topic :: Utilities',
    ]
)
