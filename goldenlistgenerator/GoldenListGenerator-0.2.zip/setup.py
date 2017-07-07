from GoldenListGenerator import __version__

try:
    from setuptools import setup
except:
    from distutils.core import setup

dependencies = ['PyYAML', 'cx_Oracle']

setup(
    name='GoldenListGenerator',
    version=".".join(str(x) for x in __version__),
    description='Generates a golden list(CSV file) using user specified fields. Program takes in two data sets from the '
                'database and finds common fields between them to generate a golden list',
    url='',
    author='Imran Ali',
    author_email='imran.ali@kapsch.net',
    install_requires=dependencies,
    packages=['GoldenListGenerator'],
    entry_points={
        'console_script':[
            'GoldenListGenerator=GoldenListGenerator.__main__:main'
        ],
    },
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
    include_package_data=True,
)