#! /bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Hiroaki Itoh <https://bitbucket.org/hhsprings/>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
# - Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
#
# - Neither the name of the xwhhsprings nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
from __future__ import unicode_literals

import os
import sys
import re
import argparse
import platform
import subprocess
from os.path import abspath, basename, splitext, dirname


__version__ = "1.0.6"
__all__ = ["caller_type", "curdir", "main"]


_SYSPLAT_WIN = ("win32", )


if sys.platform in ("win32", "msys", "cygwin"):
    _ENCODING_IN = "mbcs"
    if sys.platform in ("msys", "cygwin"):
        # msys2 and cygwin don't have mbcs codec,
        # but they have "cp*", so try to detect
        # codepage of your windows.
        _dosmes = os.environ["COMSPEC"].replace("\\", "/")
        _chcp = subprocess.check_output(
            [_dosmes, "/c", "chcp"]).decode("quopri")
        _ENCODING_IN = "cp" + re.match(r".*: (\d+)$", _chcp.strip()).group(1)

    def _decode(s):
        if not hasattr(s, "decode"):
            return s
        # unfortunately in this case, we have to try
        # to decode with two encodings because cygwin
        # and msys2 uses "utf-8" against the windows
        # system default (mbcs)!
        try:
            try:
                return s.decode()
            except UnicodeDecodeError:
                try:
                    return s.decode(_ENCODING_IN)
                except UnicodeDecodeError:
                    return s.decode("utf-8")
        except UnicodeDecodeError:
            raise
else:
    # Applying this to other than file encoding is truly
    # incorrect, but it is no problem if your system uses
    # unified encoding.
    _ENCODING_IN = sys.getfilesystemencoding()
    def _decode(s):
        if hasattr(s, "decode"):
            return s.decode(_ENCODING_IN)
        return s


def _detect_caller_type():
    def _simplify_platsys(s):
        return s.split("_")[0].lower()

    platsys = _simplify_platsys(platform.system())

    if sys.platform not in _SYSPLAT_WIN:
        # sys.platform == "cygwin" means the python interpreter was built
        # with cygwin's gcc, i.e. it's not the official CPython, and
        # if so, 'cygwin' is almost the same as *nix. (other case,
        # such as 'msys2', maybe it is the same.)
        return sys.platform, platsys, None

    # sys.platform in _SYSPLAT_WIN:
    #   i'm invoked from the official CPython Windows binary.
    #   Various cases are considerable:
    #   * user call me from cmd.exe interpreter.
    #   * user call me from cygwin's shell.
    #   * user call me from msys's shell.
    #   * user call me from msys2's shell.
    import psutil  # http://pythonhosted.org/psutil
    parent = psutil.Process().parent()
    while parent:
        if splitext(basename(sys.argv[0]))[0] != splitext(basename(parent.exe()))[0]:
            break
        parent = parent.parent()
    seppath = _decode(parent.exe()).split(os.sep)
    # first, check roughly
    maybe_cygwin = any([b.startswith("cygwin") for b in seppath])
    maybe_msys = any([b.startswith("msys") for b in seppath])
    # get detail
    if maybe_msys or maybe_cygwin:
        parent_exe = parent.exe()
        if "env.exe" == basename(parent.exe()):
            parent_exe = os.path.join(dirname(parent.exe()), "sh.exe")
        # explicitly invoking 'uname -s' is exactly the same as 'platform.system()'
        # if sys.platform is not "win32", but at here our python complains
        # 'platform.system()' is "Windows", this is not what we want.
        return _simplify_platsys(sys.platform), _simplify_platsys(
            _decode(
                subprocess.check_output(
                    [parent_exe, "-c", "uname -s"]))), parent_exe
        # msys: MINGW32_NT-6.1 -> mingw32
        # msys2: MSYS_NT-6.1  -> msys
        # cygwin: CYGWIN_NT-6.1 -> cygwin
    return sys.platform, platsys, None  # cmd.exe?


caller_type = _detect_caller_type()
del _detect_caller_type


def curdir(
    physical,
    winpath=caller_type[0] in ("win32", "msys", "cygwin") and \
        caller_type[1] not in ("mingw32", "msys", "cygwin")
    ):
    """
    Return the current directory according to the following rules:
    +---------------+-----------------------------+----------------------+
    | from          | python                      | default              |
    +===============+=============================+======================+
    | cmd.exe       | official CPython on windows | follow the behavior  |
    |               |                             | of windows native.   |
    +---------------+-----------------------------+----------------------+
    | msys          | official CPython on windows | follow the behavior  |
    | (bash, etc.)  +-----------------------------+ of MSYS.             |
    |               | msys CPython? if any,       |                      |
    +---------------+-----------------------------+----------------------+
    | msys2         | official CPython on windows | follow the behavior  |
    | (bash, etc.)  +-----------------------------+ of MSYS2.            |
    |               | msys2 CPython               |                      |
    +---------------+-----------------------------+----------------------+
    | cygwin        | official CPython on windows | follow the behavior  |
    | (bash, etc.)  +-----------------------------+ of cygwin.           |
    |               | cygwin CPython              |                      |
    +---------------+-----------------------------+----------------------+
    | *nix shell    | various                     | follow the behavior  |
    |               |                             | of *nix native.      |
    +---------------+-----------------------------+----------------------+
    Except but the case following windows native, physical=True
    corresponds to "pwd -P", physical=False corresponds to "pwd -L".

    If winpath=True, this function follow the behavior of windows native,
    even if cygwin. Of course this makes no sense on real *nix.
    
    """

    if caller_type[0] not in _SYSPLAT_WIN:
        # not windows, or unix-like emulations on windows.
        if not (caller_type[0] in ("cygwin", "msys") and winpath):
            if not physical:
                return _decode(abspath(os.environ["PWD"]))
            else:
                # os.curdir always returns "physical"
                return _decode(abspath(os.curdir))

    # windows
    if winpath and caller_type[0] not in _SYSPLAT_WIN:
        # cygwin's python and msys2's python can't travel to
        # out of their box.
        domestos = os.environ["COMSPEC"]
        if caller_type[0] not in _SYSPLAT_WIN:
            domestos = domestos.replace("\\", "/")
        return _decode(subprocess.check_output([domestos, "/c", "chdir"])).strip()

    parent_exe = caller_type[2]
    if caller_type[1].startswith("mingw") and not winpath:  # msys
        # MSYS (mingw32) cheks whether ALL of its parents are not of
        # msys application except but toplevel shell, for example:
        #   1. cmd.exe -> msys bash
        #   2. cmd.exe -> powershell -> msys bash
        #   3. cmd.exe -> win native cpython -> msys bash
        #   4. cmd.exe -> win native cpython -> msys bash -> msys bash
        #   5. cmd.exe -> msys bash -> cmd.exe -> msys bash
        # all the cases except but 1., pwd always displays windows
        # native path, not msys virtual path.
        mtt_tmp = _decode(subprocess.check_output(
            [parent_exe, "-c", "mount"])).strip()
        mtt_tmp = re.split(r"\r?\n", mtt_tmp)
        rgx = re.compile(
            r"(.*)\s+on\s+(.*)\s+type\s+.*\s+\(.*\)")
        mtt = []
        for s, t in [rgx.match(mp).group(1, 2) for mp in mtt_tmp]:
            if not s.endswith("\\"):
                s += "\\"
            if not t.endswith("/"):
                t += "/"
            mtt.append((s, t))

        mtt.sort(key=lambda mp: (-len(mp[0]), len(mp[1])))
        tmp = _decode(subprocess.check_output(
            [parent_exe, "-c", "pwd"]
            )).strip().replace("/", "\\")
        if not tmp.endswith("\\"):
            tmp += "\\"
        for s, t in mtt:
            if s.lower() in tmp.lower():
                tmp = tmp[:len(s)].lower().replace(
                    s.lower(), t) + tmp[len(s):]
        if len(tmp) > 1 and tmp[-1] in "/\\":
            tmp = tmp[:-1]
        return tmp
    return _decode(abspath(os.curdir))


def main():
    """
    commandline interface for pwdpp.
    """
    #
    from argparse import RawTextHelpFormatter
    parser = argparse.ArgumentParser(
        description="""\
Print the full filename of the current working directory.
""",
        formatter_class=RawTextHelpFormatter)
    # emulate bash builtin's pwd
    parser.add_argument(
        "-P", "--physical",
        action="store_true", default=True,
        help="""
avoid all symlinks (default).
(if your system can reveal symlinks.)

""")
    parser.add_argument(
        "-L", "--logical",
        action="store_false", dest="physical",
        help="""
use PWD from environment, even if it
contains symlinks. 
(if your system can't detect symlinks,
this option has no effect.)

""")

    # additional this script's specific.
    parser.add_argument(
        "-s", "--pathsep",
        choices=[
            "bs", "fs",
            ],
        default="bs" if caller_type[1] in _SYSPLAT_WIN else "fs",
        help="""
specify path separator.
(bs: backslash / fs: forward slash.)

""")
    parser.add_argument(
        "-W", action="store_true",
        help="""
print the Win32 value of the physical
directory. this is a simple emulation of
bash's pwd on MSYS(2). Of course, this makes
no sense on *nix.

""")
    args = parser.parse_args()
    res = curdir(args.physical, args.W)
    # i don't know you want to use this script not on windows,
    # but if so, i can't use "os.sep".
    if args.pathsep == "fs":
        res = res.replace("\\", "/")
    else:
        res = res.replace("/", "\\")
    # PYTHONIOENCODING=utf-8 pwdpp -W
    print(res)


if __name__ == '__main__':
    main()
