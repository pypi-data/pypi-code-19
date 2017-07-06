"""

"""

from setuptools import setup
from distutils.core import Command as BaseCommand
from unittest import TestLoader, TextTestRunner


class TestCommand(BaseCommand):
    """Runs the package tests."""
    description = 'Runs all package tests.'

    user_options = [
        ('junit=', None,
         'outputs results to an xml file.')
    ]

    def initialize_options(self):
        self.junit = None

    def finalize_options(self):
        pass

    def run(self):
        # Import xmlrunner here so it's not a setup requirement
        import xmlrunner
        test_suite = TestLoader().discover('.')
        if self.junit:
            with open(self.junit, 'wb') as output:
                runner = xmlrunner.XMLTestRunner(output)
                runner.run(test_suite)
        else:
            runner = TextTestRunner(verbosity=2)
            runner.run(test_suite)


setup(name='envipyengine',
      version='1.0.0',
      description='ENVI Python Engine',
      long_description='',
      author='Exelis Visual Information Solutions, Inc.',
      packages=['envipyengine',
                'envipyengine.taskengine'],
      cmdclass=dict(test=TestCommand),
      license='MIT',
      keywords='envi idl',
      package_data = {
                  'envipyengine': [
                        'doc/_modules/*.html',
                        'doc/_modules/gsf/*.html',
                        'doc/_static/*',
                        'doc/*.html',
                        'doc/*.js'
                  ]
            }
      )
