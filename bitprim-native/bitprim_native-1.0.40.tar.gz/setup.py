#!/usr/bin/env python

# 
# Copyright (c) 2017 Bitprim developers (see AUTHORS)
# 
# This file is part of Bitprim.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 

#!/usr/bin/env python
# Python binding for Keystone engine. Nguyen Anh Quynh <aquynh@gmail.com>

# upload TestPyPi package with: $ python setup.py sdist upload -r pypitest
# upload PyPi package with: $ python setup.py sdist upload -r pypi

import glob
import os
import platform
import shutil
import stat
import sys

from setuptools import setup, find_packages
from setuptools.extension import Extension

from distutils import dir_util, file_util
from distutils import log
# from distutils.command.build_clib import build_clib
# from distutils.command.install_lib import install_lib
# from distutils.command.sdist import sdist
# from distutils.core import setup

from setuptools.command.install_lib import install_lib
from setuptools.command.install import install
from setuptools.command.build_ext import build_ext
from setuptools.dist import Distribution


from conans.client.conan_api import (Conan, default_manifest_folder)


import fnmatch
import os

        
PKG_NAME = 'bitprim_native'
VERSION = '1.0.40'
SYSTEM = sys.platform

def get_similar_lib(path, pattern):
    # for file in os.listdir('.'):
    #     if fnmatch.fnmatch(file, '*.txt'):
    #         print file
    for file in os.listdir(path):
        if fnmatch.fnmatch(file, pattern):
            return file
    return ""

# class CustomInstallCommand(install):
#     """Customized setuptools install command - prints a friendly greeting."""
#     def run(self):
#         print "Hello, developer, how are you? :)"
#         install.run(self)

# class CustomInstall(install_lib):
#     def install(self):
#         print('CustomInstall.install')
#         install_lib.install(self)

#         build_ext = self.get_finalized_command('build_ext')
        

#         for key in build_ext.compiler.executables.keys():
#             # self.set_executable(key, build_ext.compiler.executables[key])
#             print("executables - key: %s, value: %s" % (key, build_ext.compiler.executables[key]))

# class build_ext_subclass( build_ext ):
#     def build_extensions(self):

#         print("build_ext_subclass.build_extensions")
#         print("self.compiler.compiler_type")
#         print(self.compiler.compiler_type)

#         for key in self.compiler.executables.keys():
#             print("executables - key: %s, value: %s" % (key, self.compiler.executables[key]))

#         # c = self.compiler.compiler_type
#         # if copt.has_key(c):
#         #    for e in self.extensions:
#         #        e.extra_compile_args = copt[ c ]
#         # if lopt.has_key(c):
#         #     for e in self.extensions:
#         #         e.extra_link_args = lopt[ c ]
#         build_ext.build_extensions(self)

# class CustomInstall(install_lib):
#     def install(self):
#         print('CustomInstall.install')
#         install_lib.install(self)
#         bitprim_install_dir = os.path.join(self.install_dir, 'bitprim/')
        
#         if not os.path.exists(bitprim_install_dir):
#             os.makedirs(bitprim_install_dir)

#         log.info("bitprim_install_dir: %s" % (bitprim_install_dir, ))
#         log.debug("bitprim_install_dir: %s" % (bitprim_install_dir, ))
#         print("bitprim_install_dir: %s" % (bitprim_install_dir, ))

#         for lib_file in SETUP_DATA_FILES:
#             log.info("lib_file: %s" % (lib_file, ))
#             log.debug("lib_file: %s" % (lib_file, ))
#             print("lib_file: %s" % (lib_file, ))

#             filename = os.path.basename(lib_file)
#             log.info("filename: %s" % (filename, ))
#             log.debug("filename: %s" % (filename, ))
#             print("filename: %s" % (filename, ))

#             dest_file = os.path.join(self.install_dir, 'bitprim', filename)

#             log.info("dest_file: %s" % (dest_file, ))
#             log.debug("dest_file: %s" % (dest_file, ))
#             print("dest_file: %s" % (dest_file, ))

#             # file_util.copy_file(lib_file, bitprim_install_dir)
#             file_util.copy_file(lib_file, dest_file)

# class MyDist(Distribution):
#      def has_ext_modules(self):
#          return True



# ------------------------------------------------

c = Conan.factory()


try:
    # c.remote_add(remote, url, verify_ssl, args.insert)
    c.remote_add('bitprim', 'https://api.bintray.com/conan/bitprim/bitprim')
except:
    print ("Conan Remote exists, ignoring exception")

refe = "."

# c.install(refe, verify=None, manifests=None)
c.install(refe, verify=None, manifests_interactive=None, manifests=None)

print('-----------------------------------------------------------------------------------')
xxx = get_similar_lib('bitprim/lib', "*boost_atomic*")
print(xxx)
print('-----------------------------------------------------------------------------------')



from sys import platform
# if platform == "linux" or platform == "linux2":
#     # linux
# elif platform == "darwin":
#     # OS X
# elif platform == "win32":
#     # Windows...

def get_libraries():
    # libraries = ['bitprim-node-cint', 'bitprim-node', 'bitprim-blockchain', 'bitprim-network', 'bitprim-consensus', 'bitprim-database', 'bitprim-core', 'boost_atomic', 'boost_chrono', 'boost_date_time', 'boost_filesystem', 'boost_iostreams', 'boost_locale', 'boost_log', 'boost_log_setup', 'boost_program_options', 'boost_random', 'boost_regex', 'boost_system', 'boost_unit_test_framework', 'boost_prg_exec_monitor', 'boost_test_exec_monitor', 'boost_thread', 'boost_timer', 'secp256k1', 'bz2', 'gmp', 'z',]
    fixed = ['bitprim-node-cint', 'bitprim-node', 'bitprim-blockchain', 'bitprim-network', 'bitprim-consensus', 'bitprim-database', 'bitprim-core']
    libraries = ['boost_atomic', 'boost_chrono', 'boost_date_time', 'boost_filesystem', 'boost_iostreams', 'boost_locale', 'boost_log', 'boost_log_setup', 'boost_program_options', 'boost_random', 'boost_regex', 'boost_system', 'boost_unit_test_framework', 'boost_prg_exec_monitor', 'boost_test_exec_monitor', 'boost_thread', 'boost_timer', 'secp256k1', 'bz2', 'gmp', 'z',]

    if platform == "win32":
        winlibs = fixed
        for lib in libraries:
            print(lib)
            xxx = get_similar_lib('bitprim/lib', "*" + lib + "*")
            if xxx != '':
                xxx = xxx.replace('.lib', '')
                print(xxx)
                winlibs.append(xxx)
    
        print(winlibs)
        return winlibs
    else:
        return fixed + libraries



    # C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Tools\MSVC\14.10.25017\bin\HostX64\x64\link.exe /nologo /INCREMENTAL:NO /LTCG /DLL /MANIFEST:EMBED,ID=2 /MANIFESTUAC:NO /LIBPATH:bitprim/lib /LIBPATH:c:\python36\libs /LIBPATH:c:\python36\PCbuild\amd64 "/LIBPATH:C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Tools\MSVC\14.10.25017\ATLMFC\lib\x64" "/LIBPATH:C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Tools\MSVC\14.10.25017\lib\x64" "/LIBPATH:C:\Program Files (x86)\Windows Kits\NETFXSDK\4.6.1\lib\um\x64" "/LIBPATH:C:\Program Files (x86)\Windows Kits\10\lib\10.0.15063.0\ucrt\x64" "/LIBPATH:C:\Program Files (x86)\Windows Kits\10\lib\10.0.15063.0\um\x64"
    # 
    #  bitprim-node-cint.lib 
    # bitprim-node.lib 
    # bitprim-blockchain.lib 
    # bitprim-network.lib 
    # bitprim-consensus.lib 
    # bitprim-database.lib 
    # bitprim-core.lib 
    # libboost_atomic-vc141-mt-s-1_64.lib 
    # libboost_chrono-vc141-mt-s-1_64.lib 
    # libboost_date_time-vc141-mt-s-1_64.lib
    # libboost_filesystem-vc141-mt-s-1_64.lib
    # libboost_iostreams-vc141-mt-s-1_64.lib
    # libboost_locale-vc141-mt-s-1_64.lib
    # libboost_log-vc141-mt-s-1_64.lib
    # libboost_log_setup-vc141-mt-s-1_64.lib
    # libboost_program_options-vc141-mt-s-1_64.lib
    # libboost_random-vc141-mt-s-1_64.lib
    # libboost_regex-vc141-mt-s-1_64.lib
    # libboost_system-vc141-mt-s-1_64.lib
    # libboost_unit_test_framework-vc141-mt-s-1_64.lib
    # libboost_prg_exec_monitor-vc141-mt-s-1_64.lib
    # libboost_test_exec_monitor-vc141-mt-s-1_64.lib
    # libboost_thread-vc141-mt-s-1_64.lib
    # libboost_timer-vc141-mt-s-1_64.lib
    # secp256k1.lib
    # zlib.lib 
    # /EXPORT:PyInit_bitprim_native 
     # build\temp.win-amd64-3.6\Release\chain/header.obj 
    # build\temp.win-amd64-3.6\Release\chain/block.obj 
    # build\temp.win-amd64-3.6\Release\chain/merkle_block.obj 
    # build\temp.win-amd64-3.6\Release\bitprimmodule.obj 
    # build\temp.win-amd64-3.6\Release\utils.obj 
    # build\temp.win-amd64-3.6\Release\chain/chain.obj 
    # build\temp.win-amd64-3.6\Release\binary.obj 
    # build\temp.win-amd64-3.6\Release\chain/point.obj 
    # build\temp.win-amd64-3.6\Release\chain/history.obj 
    # build\temp.win-amd64-3.6\Release\chain/word_list.obj 
    # build\temp.win-amd64-3.6\Release\chain/transaction.obj 
    # build\temp.win-amd64-3.6\Release\chain/output.obj 
    # build\temp.win-amd64-3.6\Release\chain/output_list.obj 
    # build\temp.win-amd64-3.6\Release\chain/input.obj 
    # build\temp.win-amd64-3.6\Release\chain/input_list.obj 
    # build\temp.win-amd64-3.6\Release\chain/script.obj
    # build\temp.win-amd64-3.6\Release\chain/payment_address.obj
    # build\temp.win-amd64-3.6\Release\chain/compact_block.obj
    # build\temp.win-amd64-3.6\Release\chain/output_point.obj
    # build\temp.win-amd64-3.6\Release\chain/block_list.obj
    # build\temp.win-amd64-3.6\Release\chain/transaction_list.obj
    # build\temp.win-amd64-3.6\Release\chain/stealth_compact.obj
    # build\temp.win-amd64-3.6\Release\chain/stealth_compact_list.obj
    # /OUT:build\lib.win-amd64-3.6\bitprim_native.cp36-win_amd64.pyd
    # /IMPLIB:build\temp.win-amd64-3.6\Release\chain\bitprim_native.cp36-win_amd64.lib
    # 
    # 
    # 
    # bitprimmodule.obj : warning LNK4197: export 'PyInit_bitprim_native' specified multiple times; using first specification
    #    Creating library build\temp.win-amd64-3.6\Release\chain\bitprim_native.cp36-win_amd64.lib and object build\temp.win-amd64-3.6\Release\chain\bitprim_native.cp36-win_amd64.exp
    # MSVCRT.lib(initializers.obj) : warning LNK4098: defaultlib 'libcmt.lib' conflicts with use of other libs; use /NODEFAULTLIB:library
    # header.obj : error LNK2001: unresolved external symbol __imp_chain_header_set_version

extensions = [
	Extension('bitprim_native',

        define_macros = [('BITPRIM_LIB_STATIC', None),],
        # 
    	sources = ['utils.c',  'chain/header.c', 'chain/block.c', 'chain/merkle_block.c', 'bitprimmodule.cpp',
        'chain/chain.c', 'binary.c', 'chain/point.c', 'chain/history.c', 'chain/word_list.c', 
        'chain/transaction.c', 'chain/output.c', 'chain/output_list.c',  'chain/input.c', 'chain/input_list.c', 
        'chain/script.c', 'chain/payment_address.c', 'chain/compact_block.c', 'chain/output_point.c',
        'chain/block_list.c', 'chain/transaction_list.c', 'chain/stealth_compact.c', 'chain/stealth_compact_list.c'],

        include_dirs=['bitprim/include'],
        library_dirs=['bitprim/lib'],
        # libraries = ['bitprim-node-cint', 'bitprim-node', 'bitprim-blockchain', 'bitprim-network', 'bitprim-consensus', 'bitprim-database', 'bitprim-core', 'boost_atomic', 'boost_chrono', 'boost_date_time', 'boost_filesystem', 'boost_iostreams', 'boost_locale', 'boost_log', 'boost_log_setup', 'boost_program_options', 'boost_random', 'boost_regex', 'boost_system', 'boost_unit_test_framework', 'boost_prg_exec_monitor', 'boost_test_exec_monitor', 'boost_thread', 'boost_timer', 'secp256k1', 'bz2', 'gmp', 'z',],
        libraries = get_libraries()



    ),
]



setup(
    # name='bitprim_native',
    # version='1.0.14',
    name=PKG_NAME,
    version=VERSION,

    description='Bitprim Platform',
    long_description='Bitprim Platform',
    url='https://github.com/bitprim/bitprim-py',

    # Author details
    author='Bitprim Inc',				#TODO!
    author_email='dev@bitprim.org',		#TODO!

    # Choose your license
    license='MIT',    					#TODO!

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        'Programming Language :: C++',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords='bitcoin litecoin cash money bitprim',

    # # You can just specify the packages manually here if your project is
    # # simple. Or you can use find_packages().
    # packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    # packages=['bitprim-node-cint'],
    # # package_dir={'bitprim-node-cint': 'src/mypkg'},
    # package_dir={'bitprim-node-cint': './'},
    # package_data={'bitprim-node-cint': ['bitprim/lib/*bitprim-node-cint.*']},
    # packages=('bitprim', ),
    # package_data={ 'bitprim': ['bitprim/lib/*bitprim-node-cint*'] },

    # packages=['bitprim-node-cint'],
    # package_data={ 'bitprim-node-cint': ['libbitprim-node-cint.so'] },

    # distclass = MyDist,

    # eager_resources=['bitprim/lib/libbitprim-node-cint.so'],

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # # List run-time dependencies here.  These will be installed by pip when
    # # your project is installed. For an analysis of "install_requires" vs pip's
    # # requirements files see:
    # # https://packaging.python.org/en/latest/requirements.html
    # install_requires=['peppercorn'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },

#   data_files = [('lib\\site-packages',['C:\\development\\bitprim\\build\\bitprim-node-cint\\bitprim-node-cint.dll'])],

	# data_files = [('lib\\site-packages', ['bitprim-node-cint\\lib\\bitprim-node-cint.dll'])],
    # data_files = [
    #     ('lib/site-packages', ['bitprim-node-cint/lib/bitprim-node-cint.*'])
    # ],

    # data_files = [
    #     ('lib/site-packages', glob.glob('bitprim-node-cint/lib/*bitprim-node-cint.*'))
    # ],


    # data_files = [
    #     ('/usr/local/lib', glob.glob('bitprim/lib/*bitprim-node-cint.*'))
    # ],


# tion="-I/home/fernando/dev/bitprim/bitprim-node-cint/include" --global-option="-L/home/fernando/dev/bitprim/build/bitprim-node-cint" -e .

    ext_modules = extensions,


    # cmdclass=dict(
    #     install_lib=CustomInstall,
    #     # install=CustomInstallCommand,
    # ),

    # cmdclass = {'build_ext': build_ext_subclass },

)
