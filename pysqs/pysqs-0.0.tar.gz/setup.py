from setuptools import setup
import os
import versioneer

try:
    from Cython.Build import cythonize
except ImportError:
    raise ImportError("Cython must be installed before pysqs can be installed.")

def readme(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='pysqs',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Brandon Bocklund',
    author_email='brandonbocklund@gmail.com',
    description='pysqs calculates simple quasirandom structures',
    packages=['pysqs'],
    ext_modules=cythonize(['pysqs/enumerate.pyx']),
    license='MIT',
    long_description=readme('README.rst'),
    url='https://brandonbockund.com/',
    install_requires=[],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 1 - Planning',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],

)
