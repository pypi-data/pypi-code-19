from setuptools import setup, find_packages


def read(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name='studentit-bookit-client',
    version='0.2.0',
    description='API client and command line application for connecting to BookIT',
    long_description=read('README.rst'),
    # The project's main homepage.
    url='https://github.com/cmbrad/studentit-bookit-client',
    # Author details
    author='Christopher Bradley',
    author_email='chris.bradley@unimelb.edu.au',
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(include=['studentit*']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=read('runtime-requirements.txt').split('\n'),
    entry_points={
        'console_scripts': [
            'bookit=bookit.cli:main',
        ],
    },
)
