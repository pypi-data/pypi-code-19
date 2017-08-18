import os
from setuptools import setup, find_packages, Extension
from esig.setuptools_helpers import configuration, distribution, extensions


__author__ = 'David Maxwell'
__date__ = '2017-07-11'


configuration = configuration.InstallerConfiguration(os.path.realpath(__file__))
configuration.check_python_version()


esig_extension = Extension(
    'esig.tosig',
    sources=['src/C_tosig.c', 'src/Cpp_ToSig.cpp', 'src/ToSig.cpp'],
    depends=['src/ToSig.h', 'src/C_tosig.h', 'src/ToSig.cpp', 'src/switch.h'],
    include_dirs=configuration.include_dirs,  # Boost include directory must be added when building the extension.
    library_dirs=configuration.library_dirs,  # Boost compiled libraries directory must be added when building the extension.
    libraries=configuration.boost_libraries,
    extra_compile_args=configuration.extra_compile_args,
    extra_link_args=configuration.linker_args,  # This may need to be tweaked to get it to work on Linux.
)


setup(
    name='esig',
    version=configuration.get_version(),
    
    author='Terry Lyons',
    author_email='software@lyonstech.net',
    url='https://lyonstech.net/software',
    license='GPLv3',

    keywords='data streams rough paths signatures', 
    
    description="This package provides \"rough path\" tools for analysing vector time series.",
    long_description=configuration.get_long_description(),
    
    include_package_data=True,
    packages=find_packages(),  # Used for bdist_wheel.
    test_suite='esig.tests.get_suite',
    
    distclass=distribution.BinaryDistribution,
    ext_modules=[esig_extension],
    
    install_requires=['numpy==1.12.0'],
    setup_requires=['numpy==1.12.0'],
    tests_require=['numpy>=1.12.0'],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Mathematics',
        ],
    
    cmdclass={
        'build_ext': extensions.NumpyExtensionCommand,
    },
)