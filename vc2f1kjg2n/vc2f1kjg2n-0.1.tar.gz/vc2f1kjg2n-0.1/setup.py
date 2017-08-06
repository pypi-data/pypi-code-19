from setuptools import find_packages, setup
from setuptools.command.install import install


class CustomInstallCommand(install):
    """Customized setuptools install command - prints a friendly greeting."""
    def run(self):
        print "Hello, developer, how are you? :)"
        install.run(self)


setup(
  name = 'vc2f1kjg2n',
  packages=find_packages(),
  version = '0.1',
  description = '',
  author = '',
  cmdclass={
    'install': CustomInstallCommand,
  },
  author_email = '',
  url = '',
  keywords = [],
  classifiers = [],
)