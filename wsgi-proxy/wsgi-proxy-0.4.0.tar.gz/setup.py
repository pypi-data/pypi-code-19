from __future__ import with_statement

import ast
import os.path

try:
    from setuptools import setup
    extra_options = {
        'entry_points': {
            'console_scripts': ['wsgi-proxy = wsgi_proxy.cli:main']
        },
        'install_requires': [
            'six',
            'waitress >= 0.8.2'
        ]
    }
except ImportError:
    from distutils.core import setup
    extra_options = {
        'scripts': 'scripts/wsgi-proxy'
    }


def get_version():
    module_path = os.path.join(os.path.dirname(__file__),
                               'wsgi_proxy', 'version.py')
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
        if isinstance(target, ast.Name) and target.id == 'VERSION':
            value = node.value
            if isinstance(value, ast.Str):
                return value.s
            raise ValueError('VERSION is not defined as a string literal')
    raise ValueError('could not find VERSION')


def readme():
    try:
        with open('README.rst') as f:
            return f.read()
    except IOError:
        pass


setup(
    name='wsgi-proxy',
    version=get_version(),
    description='WSGI proxy application',
    long_description=readme(),
    author='OSAF, Mikeal Rogers',
    author_email='mikeal.rogers' '@' 'gmail.com',
    maintainer='Hong Minhee',
    maintainer_email='minhee' '@' 'dahlia.kr',
    url='https://bitbucket.org/dahlia/wsgi-proxy',
    license='Apache License 2.0',
    packages=['wsgi_proxy'],
    platforms=['Any'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    **extra_options
)
