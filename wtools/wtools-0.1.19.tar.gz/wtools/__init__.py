#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com

import os

version = "0.1.19"
location = os.path.abspath(os.path.dirname(__file__))


def install_dirs(bld, dirs, mode=0755):
    if not bld.cmd.startswith("install"):
        return
    
    prefix = bld.env.PREFIX

    for d in dirs:
        path = os.path.join(prefix, d)
        if not os.path.exists(path):
            os.makedirs(path, mode=mode)


def get_rpath(bld, paths=['/lib', '/usr/lib', '/usr/local/lib']):

    if "NDEBUG" in bld.env.DEFINES:
        return paths

    if not bld.env.DEST_CPU in ['i386', 'i586', 'i686', 'x86_64']:
        return paths

    prefix = bld.env.PREFIX
    if not os.path.exists(prefix):
        os.makedirs(prefix)

    rpaths = ['$ORIGIN/../lib']
    pnode = bld.root.find_dir(prefix)
    epath = os.path.realpath('%s/lib' % bld.env.EROOT)    

    if epath.startswith(os.getenv("HOME")):
        epath = '$ORIGIN/%s' % bld.root.find_dir(epath).path_from(pnode)
        rpaths.append(epath)

    for lpath in bld.env.LIBPATH:
        if lpath.startswith(os.getenv("HOME")):
            lpath = '$ORIGIN/../%s' % bld.root.find_dir(lpath).path_from(pnode)
        rpaths.append(lpath)

    rpaths.extend(paths)
        
    if bld.env.LIBDIR.endswith('lib64'):
        rpaths = ["%s64" % p for p in rpaths]

    return rpaths


