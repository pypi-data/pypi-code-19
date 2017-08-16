from setuptools import setup, find_packages

setup(name='citrination',
      author='Kyle Michel',
      author_email='kyle@citrine.io',
      version='1.1.1',
      url='http://github.com/CitrineInformatics/python-citrination-cli',
      description='Command line interface for interacting with Citrination sites',
      packages=find_packages(),
      install_requires=[
            'argparse',
            'pyCLI==2.0.3',
            'citrination-client==1.5.3'
      ],
      entry_points={
            'console_scripts': [
                  'citrination=citrination.__main__:main'
            ]
      })
