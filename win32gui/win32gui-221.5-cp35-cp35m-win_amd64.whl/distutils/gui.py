import sys
import os
import shutil
import winreg

from .command import win32_build_ext
from typing import Iterator


def iter_mfc(plat_name: str) ->Iterator[str]:
    if sys.hexversion < 0x2060000:
        # hrm - there doesn't seem to be a 'redist' directory for this
        # compiler (even the installation CDs only seem to have the MFC
        # DLLs in the 'win\system' directory - just grab it from
        # system32 (but we can't even use win32api for that!)
        src = os.path.join(
            os.environ.get('SystemRoot'), 'System32', 'mfc71.dll')
        if not os.path.isfile(src):
            raise RuntimeError('Can\'t find {}'.format(src))
        yield src
    else:
        plat_dir_64 = 'x64'
        # 2.6, 2.7, 3.0, 3.1 and 3.2 all use(d) vs2008 (compiler
        # version 1500)
        if sys.hexversion < 0x3030000:
            product_key = r'SOFTWARE\Microsoft\VisualStudio\9.0\Setup\VC'
            plat_dir_64 = 'amd64'
            mfc_dir = 'Microsoft.VC90.MFC'
            mfc_files = [
                'mfc90.dll',
                'mfc90u.dll',
                'mfcm90.dll',
                'mfcm90u.dll',
                'Microsoft.VC90.MFC.manifest',
            ]
        # 3.3 and 3.4 use(d) vs2010 (compiler version 1600, crt=10)
        elif sys.hexversion < 0x3050000:
            product_key = r'SOFTWARE\Microsoft\VisualStudio\10.0\Setup\VC'
            mfc_dir = 'Microsoft.VC100.MFC'
            mfc_files = ['mfc100u.dll', 'mfcm100u.dll']
        # 3.5 and later on vs2015 (compiler version 1900, crt=14)
        else:
            product_key = r'SOFTWARE\Microsoft\VisualStudio\14.0\Setup\VC'
            mfc_dir = 'Microsoft.VC140.MFC'
            mfc_files = ['mfc140u.dll', 'mfcm140u.dll']

        # On a 64bit host, the value we are looking for is actually in
        # SysWow64Node - but that is only available on xp and later.
        access = winreg.KEY_READ
        if sys.getwindowsversion()[0] >= 5:
            access = access | 512  # KEY_WOW64_32KEY
        if plat_name == 'win-amd64':
            plat_dir = plat_dir_64
        else:
            plat_dir = 'x86'
        # Find the redist directory.
        vckey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, product_key, 0,
                               access)
        val, val_typ = winreg.QueryValueEx(vckey, 'ProductDir')
        mfc_dir = os.path.join(val, 'redist', plat_dir, mfc_dir)
        if not os.path.isdir(mfc_dir):
            raise RuntimeError(
                'Can\'t find the redist dir at {}'.format(mfc_dir))
        for f in mfc_files:
            yield os.path.join(mfc_dir, f)


class win32gui_build_ext(win32_build_ext):
    def run(self) -> None:
        super().run()
        target = os.path.join(self.build_lib, 'win32')
        try:
            for mfc in iter_mfc(self.plat_name):
                # This looks like it could be replaced by shutil.copy
                # Howver, that approach resulted in a permission error
                with open(os.path.join(target, os.path.basename(mfc)),
                          'wb+') as fd:
                    with open(mfc, 'rb') as fs:
                        shutil.copyfileobj(fs, fd)
        except:
            print('warning: unable to copy MFC DLLs')
