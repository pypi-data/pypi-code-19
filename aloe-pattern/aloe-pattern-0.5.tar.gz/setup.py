from setuptools import setup, find_packages

setup(
    name='aloe-pattern',
    version='0.5',
    description='Aloe pattern CLI',
    author='Sage Gerard',
    author_email='sage@sagegerard.com',
    license='MIT',
    keywords='css scss sass aloe plant',
    packages=find_packages(),
    test_suite='nose.collector',
    tests_require=[
        'nose'
    ],
    install_requires=[
        'libsass',
    ],
    entry_points = {
        'console_scripts': ['aloe=aloe.cli:main'],
    },
)
