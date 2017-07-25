from setuptools import setup, find_packages


def readme():
    with open('README.rst') as f:
        return f.read().strip()


def version():
    with open('VERSION') as f:
        return f.read().strip()


def requirements():
    with open('requirements.txt') as f:
        return f.read().strip().split('\n')

setup(name='diff2d',
      author='Mirko Maelicke',
      author_email='mirko.maelicke@kit.edu',
      license='CC BY-NC 4.0',
      version=version(),
      description='Module for calculating 2D Diffusion.',
      long_description=readme(),
      include_package_data=True,
      packages=find_packages(),
      install_requires=requirements(),
      zip_safe=False,
      test_suite='nose.collectors',
      tests_require=['nose']
)