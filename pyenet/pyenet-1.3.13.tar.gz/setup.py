from distutils.core import setup
from distutils.extension import Extension
from distutils.core import run_setup

import os
import glob
import sys

source_files = ["enet.pyx"]

_enet_files = glob.glob("enet/*.c")
lib_version = "1.3.13"

from distutils.command.build_ext import build_ext as _build_ext
class build_ext(_build_ext):
    def run(self):

        from Cython.Build import cythonize
        self.extensions = cythonize(self.extensions)

        _build_ext.run(self)

        extra_args = sys.argv[2:]
        run_setup(os.path.join(os.getcwd(), "setup.py"), ['build_py'] + extra_args)


if not _enet_files:

    import tarfile
    try:
        import urllib as urllib_request
    except ImportError:
        import urllib.request as urllib_request

    enet_dir = "enet-%s/" % lib_version
    enet_file = "enet-%s.tar.gz" % lib_version
    enet_url = "http://enet.bespin.org/download/%s" % enet_file

    if not os.path.isfile(enet_file):
        print("Downloading enet")

        # begin code shamelessly stolen from StackOverflow
        # http://stackoverflow.com/a/13895723/2730399
        # Answer by https://stackoverflow.com/users/4279/j-f-sebastian
        def reporthook(blocknum, blocksize, totalsize):
            readsofar = blocknum * blocksize
            if totalsize > 0:
                percent = readsofar * 1e2 / totalsize
                s = "\r%5.1f%% %*d / %d" % (percent, len(str(totalsize)),
                                            readsofar, totalsize)
                sys.stderr.write(s)
                if readsofar >= totalsize:  # near the end
                    sys.stderr.write("\n")
            else:  # total size is unknown
                sys.stderr.write("read %d\n" % (readsofar, ))

        urllib_request.urlretrieve(enet_url, enet_file, reporthook)
        print("Finished downloading enet")
        # end code shamelessly stolen from StackOverflow

    print("Unpacking enet")
    tar = tarfile.open(enet_file)

    l = len(enet_dir)
    members = []
    for member in tar.getmembers():
        if member.path.startswith(enet_dir):
            member.path = member.path[l:]
            members.append(member)

    tar.extractall('enet', members=members)
    tar.close()
    print("Finished unpacking enet")

source_files.extend(_enet_files)

define_macros = [('HAS_POLL', None), ('HAS_FCNTL', None),
                 ('HAS_MSGHDR_FLAGS', None), ('HAS_SOCKLEN_T', None)]

libraries = []

if sys.platform == 'win32':
    define_macros.extend([('WIN32', None)])
    libraries.extend(['ws2_32', 'Winmm'])

if sys.platform != 'darwin':
    define_macros.extend([('HAS_GETHOSTBYNAME_R', None),
                          ('HAS_GETHOSTBYADDR_R', None)])

ext_modules = [
    Extension(
        "enet",
        extra_compile_args=["-O3"],
        sources=source_files,
        include_dirs=["enet/include/"],
        define_macros=define_macros,
        libraries=libraries)
]

setup(
    name='pyenet',
    # packages=['enet'],
    description='A python wrapper for the ENet library',
    url='https://github.com/piqueserver/pyenet/',
    maintainer='Andrew Resch, Piqueserver team',
    maintainer_email='samuel@swalladge.id.au',

    version=lib_version,
    cmdclass={'build_ext': build_ext},
    ext_modules=ext_modules,
    requires=['Cython'],
)
