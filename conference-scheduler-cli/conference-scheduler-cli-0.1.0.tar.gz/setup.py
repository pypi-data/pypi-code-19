import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


setup(
    name='conference-scheduler-cli',
    version='0.1.0',
    license='MIT license',
    description='A command line tool to manage the schedule for a conference',
    long_description='%s\n%s' % (
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub(
            '', read('README.rst')),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    ),
    author='The UK Python Association',
    author_email=('owen.campbell@uk.python.org'),
    url='https://github.com/pyconuk/conferencescheduler-cli',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    entry_points={
        'console_scripts': [
            'scheduler = scheduler.cli:scheduler',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Utilities',
    ],
    install_requires=[
        'click >= 6.7',
        'conference-scheduler >= 2.1.2',
        'daiquiri >= 1.2.1',
        'python-slugify >= 1.2.4',
        'ruamel.yaml >= 0.15.23'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    python_requires=">=3.6",
)
