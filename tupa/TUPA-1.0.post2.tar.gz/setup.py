#!/usr/bin/env python

from distutils.core import setup
import os

setup(name='TUPA',
      version='1.0~2',
      install_requires=["dynet>=1.1,<2.0.0", "spacy>=1.8.2,<2.0.0"],
      description='Transition-based UCCA Parser',
      author='Daniel Hershcovich',
      author_email='danielh@cs.huji.ac.il',
      url='https://github.com/huji-nlp/tupa',
      packages=['ucca', 'tupa', 'classifiers', 'nn', 'linear', 'features', 'states'],
      package_dir={
          'ucca': os.path.join('ucca', 'ucca'),
          'tupa': 'tupa',
          'classifiers': os.path.join('tupa', 'classifiers'),
          'linear': os.path.join('tupa', 'classifiers', 'linear'),
          'nn': os.path.join('tupa', 'classifiers', 'nn'),
          'features': os.path.join('tupa', 'features'),
          'states': os.path.join('tupa', 'states'),
          },
      )
