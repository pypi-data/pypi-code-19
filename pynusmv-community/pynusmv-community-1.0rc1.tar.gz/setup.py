'''
This is the script that permits the installation of the `pynusmv_community` 
tool. This tool was developed in order to analyze and understand the community 
structure of bounded model checking instances.

.. requirements::

    + `pynusmv` to process NuSMV models and generate the BMC instances
    + `python-igraph` to produce and analyze graphs (ie. compute q-score)
    + `pycairo` to be able to render the graphs and save them to file (provided through cairocffi)
    + `pandas` to analyze the statistics gathered
    + `mathplotlib` to plot nice charts of the wordclouds and statistics
    + `wordcloud` to generate the wordcoulds that are used to analyze the communities
    + `argparse` to handle the command line arguments appropriately
    + `pymining` to mine the frequent patterns
'''

from setuptools import setup, find_packages

REQUIREMENTS = [
    'pynusmv',
    'python-igraph',
    'cairocffi',#'pycairo', -- see https://stackoverflow.com/questions/12072093/python-igraph-plotting-not-available
    'pandas',
    'matplotlib',
    'wordcloud',
    'argparse',
    'pymining',
    'concepts'
]

setup(name             = 'pynusmv-community',
      version          = '1.0rc1',
      author           = "Xavier GILLARD",
      author_email     = "xavier.gillard@uclouvain.be",
      url              = "http://lvl.info.ucl.ac.be/Tools/PyNuSMV-community",
      description      = "Tools to analyze and understand the community structure of BMC instances",
      packages         = find_packages(),
      install_requires = REQUIREMENTS,
      entry_points     = {
        'console_scripts' : [
            'commu=pynusmv_community.main:main'
        ] 
      },
      package_data     = {
          'pynusmv_community' : ['data/graph_vis/index.html',
                                 'data/graph_vis/main.js',
                                 'data/graph_vis/data/*',
                                 'data/graph_vis/lib/*.js',
                                 'data/graph_vis/styles/*.css',
                                 
                                 'data/table_vis/index.html',
                                 'data/table_vis/main.js',
                                 'data/table_vis/data/*',
                                 'data/table_vis/lib/*.js',
                                 'data/table_vis/styles/*.css',
                                ]
      },
      # TESTS
      test_suite       = 'nose.collector',
      tests_require    = ['nose'] )