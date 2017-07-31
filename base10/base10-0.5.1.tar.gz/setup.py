from setuptools import setup

setup(
    name='base10',
    version='0.5.1',
    packages=('base10',),
    url='https://github.com/mattdavis90/base10',
    license='MIT',
    author='Matt Davis',
    author_email='mattdavis90@googlemail.com',
    install_requires=('six'),
    tests_require=(),
    description=(
        'Base10 is a metrics abstractoin layer for linking multiple '
        'metrics source and stores. It also simplifies metric creation '
        'and proxying.'),
    classifiers=('License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.2',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: Implementation :: CPython',
                 'Programming Language :: Python :: Implementation :: PyPy'))
