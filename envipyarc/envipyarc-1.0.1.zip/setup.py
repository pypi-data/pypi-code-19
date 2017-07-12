"""

"""
from distutils.core import Command as BaseCommand
from unittest import TestLoader, TextTestRunner
from setuptools import setup


class TestCommand(BaseCommand):
    """Runs the package tests."""
    description = 'Runs all package tests.'

    user_options = [
        ('junit=', None,
         'outputs results to an xml file.'),
        ('pattern=', None,
         'The test pattern. Defaults to test*.py')
    ]

    def initialize_options(self):
        self.junit = None
        self.pattern = 'test*.py'

    def finalize_options(self):
        pass

    def run(self):
        # Import xmlrunner here so it's not a setup requirement
        import xmlrunner
        test_suite = TestLoader().discover('.', pattern=self.pattern)
        if self.junit:
            with open(self.junit, 'wb') as output:
                runner = xmlrunner.XMLTestRunner(output)
                runner.run(test_suite)
        else:
            runner = TextTestRunner(verbosity=2)
            runner.run(test_suite)


setup(name='envipyarc',
      version='1.0.1',
      description='ENVI Python Tools for ArcGIS',
      long_description='',
      author='Exelis Visual Information Solutions, Inc.',
      packages=['envipyarc',
                'envipyarc.templates'],
      install_requires=['envipyengine', 'envipyarclib'],
      cmdclass=dict(test=TestCommand),
      license='MIT',
      keywords='envi idl',
      scripts=['scripts/createenvitoolbox.py'],
      package_data={'envipyarc': [
          'esri/toolboxes/*.pyt',
          'esri/toolboxes/*.xml'
          ]
      }
)
