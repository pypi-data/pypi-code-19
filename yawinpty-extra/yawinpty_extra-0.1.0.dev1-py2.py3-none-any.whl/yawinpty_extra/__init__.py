from yawinpty import *
import win32api, win32con

def _dup_create(hdl):
    """dup then create PyHANDLE from an integer"""
    cur_process = win32api.GetCurrentProcess()
    return win32api.DuplicateHandle(cur_process, hdl, cur_process, 0, win32con.FALSE, win32con.DUPLICATE_SAME_ACCESS)

OldPty = Pty
class Pty(OldPty):
    def agent_process(self):
        """get agent_process"""
        return _dup_create(self._get_handles()[0])
    def subprocess(self):
        """get subprocess"""
        return _dup_create(self._get_handles()[1])
    def subthread(self):
        """get subthread"""
        return _dup_create(self._get_handles()[2])

__version__ = '0.1.0.dev1'
