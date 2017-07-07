from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import find_packages, setup

requires = [
    'xmltodict',
    'requests',
]

setup(
    name='pymental',
    version='0.0.5',
    description='Client library for interacting with Elemental Conductor',
    author='PBS Core Services Team',
    author_email='pbsi-team-core-services@pbs.org',
    url='https://github.com/pbs/pymental',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
    ],
    keywords='pymental elemental conductor client',
)
