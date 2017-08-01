import contextlib
import os
import re
import setuptools
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import shutil
import subprocess
import sys


def base_path():
    return os.path.dirname(os.path.realpath(__file__))

@contextlib.contextmanager
def cd(path):
   original_dir = os.getcwd()
   os.chdir(path)
   try:
       yield
   finally:
       os.chdir(original_dir)

def check_call(command):
    print("Running command: {}".format(command))
    subprocess.check_call(command, shell=True)

def file_replace(original_path, match, replace):
    backup_path = original_path + ".bak"
    if os.path.exists(backup_path):
        return

    shutil.copyfile(original_path, backup_path)

    original = open(original_path).readlines()
    with open(original_path, "w") as replaced_file:
        for line in original:
            replaced_line = re.sub(match, replace, line)
            replaced_file.write(replaced_line)


##############################################################################################################
############################################  original SeqLib    #############################################
##############################################################################################################

def modify_seqlib():
    """
    for some reason, bwa and htslib produce compiled object files without the PIC (position-independent code) 
    flag enabled; this means that SeqLib incorporating the original bwa/htslib cannot be linked against
    from a shared library extension; to get around this, we add the -fPIC flag option to the Makefile
    for those two projects before compiling them
    """
    cflags_line_re = r"^(CFLAGS *=.*)$"
    replacement_pattern = r"\1 -fPIC"

    htslib_makefile_path = os.path.join(base_path(), "lib/SeqLib", "htslib", "Makefile")
    file_replace(htslib_makefile_path, cflags_line_re, replacement_pattern)

    htslib_makefile_path = os.path.join(base_path(), "lib/SeqLib", "bwa", "Makefile")
    file_replace(htslib_makefile_path, cflags_line_re, replacement_pattern)

def compile_seqlib():
    seqlib_dir = os.path.join(base_path(), "lib/SeqLib")

    with cd(seqlib_dir):
        libs = ["bwa", "fml", "hts", "seqlib"]
        exist = True
        for lib in libs:
            exist &= os.path.exists("bin/lib{}.a".format(lib))
        if exist:
            return

        check_call("./configure CFLAGS=-fPIC CXXFLAGS=-fPIC")
        check_call("make")
        check_call("make install")



##############################################################################################################
###############################################    pyseqlib    ###############################################
##############################################################################################################


__version__ = '0.0.6'


class get_pybind_include(object):
    """Helper class to determine the pybind11 include path
    The purpose of this class is to postpone importing pybind11
    until it is actually installed, so that the ``get_include()``
    method can be invoked. """

    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        import pybind11
        return pybind11.get_include(self.user)


# As of Python 3.6, CCompiler has a `has_flag` method.
# cf http://bugs.python.org/issue26689
def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.cpp') as f:
        f.write('int main (int argc, char **argv) { return 0; }')
        try:
            compiler.compile([f.name], extra_postargs=[flagname])
        except setuptools.distutils.errors.CompileError:
            return False
    return True


def cpp_flag(compiler):
    """Return the -std=c++[11/14] compiler flag.
    The c++14 is prefered over c++11 (when it is available).
    """
    if has_flag(compiler, '-std=c++14'):
        return '-std=c++14'
    elif has_flag(compiler, '-std=c++11'):
        return '-std=c++11'
    else:
        raise RuntimeError('Unsupported compiler -- at least C++11 support '
                           'is needed!')


class BuildPybind11Ext(build_ext):
    """A custom build extension for adding compiler-specific options."""
    c_opts = {
        'msvc': ['/EHsc'],
        'unix': [],
    }

    if sys.platform == 'darwin':
        c_opts['unix'] += ['-stdlib=libc++', '-mmacosx-version-min=10.7']

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        if ct == 'unix':
            opts.append('-DVERSION_INFO="%s"' % self.distribution.get_version())
            opts.append(cpp_flag(self.compiler))
            if has_flag(self.compiler, '-fvisibility=hidden'):
                opts.append('-fvisibility=hidden')
        elif ct == 'msvc':
            opts.append('/DVERSION_INFO=\\"%s\\"' % self.distribution.get_version())
        for ext in self.extensions:
            ext.extra_compile_args = opts
        build_ext.build_extensions(self)

class CompileThenBuildPybind11Ext(BuildPybind11Ext):
    def build_extension(self, ext):
        modify_seqlib()
        compile_seqlib()

        super().build_extension(ext)

# import pysam

ext_modules = [

    # direct bam1_t conversion from c++ seqlib to pysam AlignedSegment:
    # this was a reasonable idea, and actually worked on mac with clang
    # but unfortunately doesn't seem to work on linux (possibly because
    # we need to compile with the -fPIC option when using gcc?)
    # 
    # it's possible that we could get it to work simply by passing the 
    # values within the bam1_t from c++ to cython (I'm guessing that 
    # the structs are ordered differently between the -fPIC-compiled 
    # version of htslib we have to use for seqlib compared to the 
    # version compiled without -fPIC used by pysam; but just a guess)
    #
    # also note that it's not obvious how we'd get two extensions to 
    # compile with two different build systems, as cmdclass is defined
    # below by package type, and there's nothing built-in to distinguish
    # a cython Extension from a pybind11 extension; this would require
    # some research in the setuptools/distutils code to see how best
    # to get this to work (gah, setuptools be mega-bad)
    #
    # Extension(
    #     "seqlib_to_pysam",
    #     sources=["seqlib_to_pysam/seqlib_to_pysam.pyx"],
    #     extra_link_args=pysam.get_libraries(),
    #     include_dirs=pysam.get_include(),
    #     ),

    Extension(
        'seqlib._seqlib',
        ['src/seqlib/seqlib.cpp'],
        include_dirs=[
            # Path to pybind11 headers
            get_pybind_include(),
            get_pybind_include(user=True),

            os.path.join(base_path(), "lib/SeqLib"),
            os.path.join(base_path(), "lib/SeqLib/htslib")
        ],
        extra_link_args=[
            os.path.join(base_path(), "lib/SeqLib/bin/libseqlib.a"),
            os.path.join(base_path(), "lib/SeqLib/bin/libbwa.a"),
            os.path.join(base_path(), "lib/SeqLib/bin/libfml.a"),
            os.path.join(base_path(), "lib/SeqLib/bin/libhts.a"),
            "-lz"
        ],
        language='c++'
    ),
]

setup(
    name='seqlib',
    version=__version__,
    author='Noah Spies',
    description='provide an in-memory interface to bwa mem',
    long_description='wraps SeqLib to allow python scripts to run bwa mem in-memory (maintaining and'
                     ' updating the index in memory in addition to actually aligning reads)',
    ext_modules=ext_modules,
    install_requires=["pybind11>=1.7", "pysam"],
    cmdclass={'build_ext': CompileThenBuildPybind11Ext},
    package_dir={"": "src"},
    packages=["seqlib"],
    zip_safe=False,
)

