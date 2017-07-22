import sys

if sys.version_info.major < 3:
    print("Please use python3")
    sys.exit()

try:
    import pypandoc
    readme = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError, RuntimeError):
    readme = open('README.md').read()

from setuptools import setup
setup(
    name='eddy',
    version='0.2.9',
    description='Static site generator with markdown support',
    long_description = readme,
    url='https://github.com/joajfreitas/eddy',
    download_url = 'https://github.com/joajfreitas/eddy',
    author="joajfreitas",
    author_email="joaj.freitas@gmail.com",
    license='GPLv3',
    packages = ['eddy', 'eddy.tools', 'eddy.md_extensions'],
    install_requires = ['pypandoc',
                        'argparse',
                       ],
    entry_points = {
        'console_scripts': ['eddy = eddy:main', 'eddy_quickstart = eddy.tools.eddy_quickstart:main',
'eddy_fetch = eddy.tools.eddy_fetch:main']},
    test_suite='nose.collector',
    tests_require=['nose'],
)
