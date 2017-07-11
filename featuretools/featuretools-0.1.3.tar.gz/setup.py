import warnings
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext as _build_ext
import os


# Bootstrap numpy install
class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process:
        __builtins__.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())

try:
    from Cython.Build import cythonize
    HAVE_CYTHON = True
except ImportError as e:
    HAVE_CYTHON = False
    warnings.warn(e.message)

ext = '.pyx' if HAVE_CYTHON else '.c'
source_dir = 'featuretools/cython_utils/pandas_backend'
if HAVE_CYTHON:
    sources = [source_dir + '/*'+ext]
else:
    abs_files = [os.path.join(os.path.abspath(source_dir), f)
                 for f in os.listdir(source_dir)]
    sources = [f for f in abs_files if os.path.isfile(f) and f.endswith(ext)]

extensions = [Extension(os.path.join(source_dir, 'utils').replace('/', '.'),
                        sources=sources)
              ]
if HAVE_CYTHON:
    extensions = cythonize(extensions)

setup(
    name='featuretools',
    version='0.1.3',
    packages=find_packages(),
    description='a framework for automated feature engineering',
    url='http://featuretools.com',
    license='BSD 4-clause',
    author='Feature Labs, Inc.',
    author_email='support@featurelabs.com',
    classifiers=[
       'Development Status :: 3 - Alpha',
       'Intended Audience :: Developers',
       'Programming Language :: Python :: 2.7'],
    install_requires=['numpy>=1.11.0',
                      'scipy>=0.17.0',
                      'pandas==0.20.1',
                      'scikit-learn>=0.18',
                      'tqdm>=4.8.4',
                      "seaborn>=0.7.1",
                      "toolz>=0.8.2",
                      "dask[complete]==0.14.3",
                      "boto>=2.46.1",
                      "boto3>=1.4.4",
                      "matplotlib>=1.5.3",
                      ],
    setup_requires=['pytest-runner>=2.0,<3dev', 'numpy>=1.11.0'],
    python_requires='>=2.7, <3',
    cmdclass={'build_ext': build_ext},
    ext_modules=extensions,
    test_suite='featuretools/tests',
    tests_require=['pytest>=3.0.1', 'mock==2.0.0'],
    keywords='feature engineering data science machine learning'
)
