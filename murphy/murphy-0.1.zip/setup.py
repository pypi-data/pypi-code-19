'''
setup
'''
import nose
from setuptools import setup, find_packages

if nose:
    setup(
        name="murphy",
        version="0.1",
        packages=find_packages(),
        description="Generic tools to identify overlapping genomic regions",
        long_description='''
The intervalTree class is an adaptation of the interval tree algorithm based on
red-black trees from Introduction to Algorithms by Cormen, Leiserson, Rivest
and Stein (2001) 2nd Edition, The MIT Press

This makes a nice self-balancing tree.  The alrogithm may be more efficient
if items are randomly selected for insertion, instead of in sort order.

I've modified the CLRS algorithm to report all overlapping nodes instead of
only the first node.  This involved adding a min value instead of only a max
value in order to speed up the search by checking if the subtree min,max
overlaps with the search interval.  The search routine is also recursive.
''',
        author="Suzy Stiegelmeyer",
        author_email="drsuuzzz@gmail.com",
        url="https://github.com/drsuuzzz/murphy",
        license="Apache-2.0",
        keywords=["bioinformatics",
                  "interval overlap tree",
                  "binary tree",
                  "genomics"],
        classifiers=["Development Status :: 3 - Alpha",
                     "Intended Audience :: Science/Research",
                     "License :: OSI Approved :: Apache Software License",
                     "Operating System :: OS Independent",
                     "Programming Language :: Python :: 2.7",
                     "Programming Language :: Python :: 3",
                     "Topic :: Scientific/Engineering :: Bio-Informatics"
                     ],
        zip_safe=False,
        test_suite="nose.collector",
        package_data={
            'murphy': ['*.gtf', '*.txt', '*.rst'],
            'murphy.tests': ['*.gtf'],
        },
        install_requires=['matplotlib'],
        )
