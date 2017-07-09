from setuptools import find_packages, setup

setup(
    name='ToxTest',
    version='0.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],

    author='Victor Jimenez',
    author_email='betabandido@gmail.com',
    description='This is an Example Package',
    license='PSF',
    keywords='hello world example examples',
    url='http://example.com',
)

