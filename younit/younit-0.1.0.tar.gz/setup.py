from setuptools import setup
import os
import sys
PY_VER = sys.version_info

if not PY_VER >= (3, 6):
    raise RuntimeError("younit doesn't support Python earlier than 3.6")

here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(here, 'younit', '__version__.py'), 'r') as f:
    exec(f.read(), about)

def read(fname):
    with open(os.path.join(here, fname), 'r') as f:
        return str(f.read().strip())

setup(
    name='younit',
    version=about['__version__'],
    packages=['younit'],
    description="a collection of helpers for the unittest module",
    long_description='\n\n'.join((read('README.rst'), read('CHANGELOG.rst'))),
    include_package_data=True,
    install_requires=[
        
    ],
    zip_safe=False,
    author="Jeremy Arr",
    author_email="jeremyarr@gmail.com",
    license="MIT",
    keywords=["asyncio","unittest","mock","testing"],
    url="https://github.com/jeremyarr/younit",
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6',
    ]
)

