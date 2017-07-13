from setuptools import setup, find_packages

version = '0.3'

def read(name):
    with open(name, 'r') as f:
        return f.read()

long_description = (
    read('README.rst')
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    read('CONTRIBUTORS.rst')
    + '\n' +
    read('CHANGES.rst')
    + '\n'
)


setup(name='zope.schemaevent',
      version=version,
      description="Event subscribers for zope.schema",
      long_description=long_description,
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: Implementation :: CPython",
          "Programming Language :: Python :: Implementation :: PyPy",
          "Framework :: Zope3",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='zope schema event',
      author='Jean-Francois Roche',
      author_email='jfroche@affinitic.be',
      url='https://github.com/zopefoundation/zope.schemaevent',
      license='gpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['zope'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.component',
          'zope.schema',
      ],
      extras_require={
          'test': [
              'zope.configuration',
              'zope.testing',
              'zope.testrunner',
          ],
      },
)
