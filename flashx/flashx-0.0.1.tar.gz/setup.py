from distutils.core import setup, Extension
from distutils.command.build_clib import build_clib
from Cython.Build import cythonize
from Cython.Distutils import build_ext
from glob import glob
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

# For C++ libraries
libsafs = ("safs",
        {"sources": glob(os.path.join("flashx/libsafs/", "*.cpp"))})
libmatrix = ('matrix',
        {'sources': glob(os.path.join("flashx/matrix/", "*.cpp"))})

# Minimum libraries we will build
libraries = [libsafs, libmatrix]

class flashpy_clib(build_clib, object):
    def initialize_options(self):
        super(flashpy_clib, self).initialize_options()
        self.include_dirs = [ "flashx/libsafs", "flashx/matrix" ]
        self.define = [
                ("BOOST_LOG_DYN_LINK", None),
                ("BIND", None), ("LINUX", None)
                ]

    def build_libraries(self, libraries):
        for (lib_name, build_info) in libraries:
            sources = build_info.get('sources')
            if sources is None or not isinstance(sources, (list, tuple)):
                raise DistutilsSetupError, \
                        ("in 'libraries' option (library '%s'), " +
                                "'sources' must be present and must be " +
                                "a list of source filenames") % lib_name
            sources = list(sources)

            print "building '%s' library" % lib_name

            # First, compile the source code to object files in the library
            # directory.  (This should probably change to putting object
            # files in a temporary build directory.)
            macros = build_info.get('macros')
            include_dirs = build_info.get('include_dirs')

            # pass flasgs to compiler
            extra_preargs = ["-std=c++11", "-O3", "-Wno-unused-function"]
            extra_preargs.append("-fopenmp")

            objects = self.compiler.compile(sources,
                    output_dir=self.build_temp,
                    macros=macros,
                    include_dirs=include_dirs,
                    debug=self.debug,
                    extra_preargs=extra_preargs)

            # Now "link" the object files together into a static library.
            # (On Unix at least, this isn't really linking -- it just
            # builds an archive.  Whatever.)
            self.compiler.create_static_lib(objects, lib_name,
                    output_dir=self.build_clib,
                    debug=self.debug)

extra_compile_args = ["-std=c++11", "-O3", "-fPIC",
        "-Wno-attributes", "-Wno-unused-variable",
        "-Wno-unused-function", "-Iflashx/","-Iflashx/libsafs", "-Iflashx/matrix",
        "-DBOOST_LOG_DYN_LINK", "-fopenmp",
        "-I/usr/local/lib/python2.7/dist-packages/numpy/core/include",
        "-I/usr/include/python2.7",
        "-DBIND", "-DLINUX"]

extra_link_args=[ "-lpthread", "-lnuma", "-fopenmp", "-lboost_log" ]

ext_modules = cythonize(Extension(
    "flashx.mat",                                # the extension name
    sources=["flashx/mat.pyx", "flashx/MatrixWrapper.cpp"], # the Cython source and
    # additional C++ source files
    include_dirs = [ "flashx/libsafs", "flashx/matrix" ],
    libraries = ["hwloc", "cblas", "aio", "numa"],
    language="c++",                               # generate&compile C++ code
    extra_compile_args=['-fopenmp', '-std=c++11', '-O0'],
    extra_link_args=extra_link_args,
    ))

setup(
    name="flashx",
    version="0.0.1",
    description="A parallel and scalable library for matrix operations",
    long_description="FlashPy parallelizes and scales the API in NumPy, " +\
            "and the algorithms in SciPy. It extends " +\
            "memory capacity with SSDs and is optimized for NUMA machines",
    url="https://github.com/flashxio/FlashX",
    author="Da Zheng",
    author_email="dzheng5@jhu.edu",
    license="Apache License, Version 2.0",
    keywords="parallel scalable machine-learning NumPy SciPy",
    install_requires=[
        "numpy",
        "Cython==0.23.5",
        "cython==0.23.5",
        ],
    package_dir = {"flashx": os.path.join("flashx/")},
    packages=["flashx", "flashx.linalg", "flashx.sparse"],
    libraries =libraries,
    cmdclass = {'build_clib': flashpy_clib, 'build_ext': build_ext},
    ext_modules = ext_modules,
)
