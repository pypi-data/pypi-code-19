''' setup.py: set up bibreduce '''

from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='princeton-bibreduce',
      version='0.2',
      description='Reduce authors/titles/links in .bib files',
      long_description=readme(),
      author='Alex Tait',
      author_email='atait@princeton.edu',
      license='MIT',
      packages=['bibreduce'],
      install_requires=[
          'bibtexparser'
      ],
      scripts=['bin/princeton-bibreduce'],
      entry_points={
          'console_scripts': ['bibreduce=bibreduce.bibreduce:cmMain'],
      },
      zip_safe=False)
