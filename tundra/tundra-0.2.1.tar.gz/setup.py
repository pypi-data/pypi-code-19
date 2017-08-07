import re

from setuptools import find_packages, setup


def make_long_description():
    with open('README.md') as f:
        readme = f.read()

    return re.sub(
        r'- \[(.*)\]\(.*\)',
        r'\1',
        readme,
    )


desc = """
Tundra
======

Pure Python, no dependencies Graph Algorithms module

Installing
----------

``pip install tundra``

Overview
--------

Structures
~~~~~~~~~~

-  Graph class
-  Digraph class

Algorithms
~~~~~~~~~~

Search
^^^^^^

-  Depth-first search
-  Breadth-first search

Spanning tree
^^^^^^^^^^^^^

-  Kruskal's Algorithm
-  Prim's Algorithm

Path
^^^^

-  Dijskra's Algoritm
-  Floyd-Warshall Algoritm
-  Nearest-neighbors hamiltonian cycle

Miscellaneous
^^^^^^^^^^^^^

-  Fringe
-  Greedy coloring
-  Proprety tests (is\_tree, is\_complete,
   ...)

Utilities
~~~~~~~~~

-  DOT language conversion
-  Export Graph to PNG
"""


setup(
    name='tundra',
    version='0.2.1',
    packages=find_packages(),

    description='Pure Python, no dependencies Graph Algorithms module',
    long_description=desc,
    url='https://github.com/caiopo/tundra',

    author='Caio Pereira Oliveira',
    author_email='caiopoliveira@gmail.com',

    license='MIT',
    copyright='Copyright 2017 Caio Pereira Oliveira',

    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.6',
    )
)
