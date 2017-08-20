"""
@brief      test log(time=1s)
"""
import os
import sys
import unittest
import warnings

if sys.version_info[0] == 2:
    from Tkinter import TclError
else:
    from tkinter import TclError

try:
    import src
except ImportError:
    path = os.path.normpath(
        os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "..",
                "..")))
    if path not in sys.path:
        sys.path.append(path)
    import src

from pyquickhelper.loghelper.flog import fLOG
from pyquickhelper.pycode import fix_tkinter_issues_virtualenv
from src.tkinterquickhelper.funcwin import open_window_params, open_window_function
from src.tkinterquickhelper.funcwin.function_helper import get_function_list, private_get_function


def my_tst_function(a, b):
    """
    return a+b
    @param      a   (float) float
    @param      b   (float) float
    @return         a+b
    """
    return (a or 1) + (b or 1)


class TestWindows (unittest.TestCase):

    def test_open_window_params(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        fix_tkinter_issues_virtualenv(fLOG=fLOG)
        params = dict(p1="p1", p2=3)
        try:
            win = open_window_params(params, do_not_open=True)
        except TclError as e:
            warnings.warn("TclError" + str(e))
            return
        fLOG(type(win))
        assert isinstance(
            win,
            src.tkinterquickhelper.funcwin.frame_params.FrameParams)

    def test_open_window_function(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        fix_tkinter_issues_virtualenv(fLOG=fLOG)
        func = my_tst_function
        try:
            win = open_window_function(func, do_not_open=True)
        except TclError as e:
            warnings.warn("TclError" + str(e))
            return
        fLOG(type(win))
        assert isinstance(
            win,
            src.tkinterquickhelper.funcwin.frame_function.FrameFunction)
        win.refresh()
        win.update()
        win.run_function(0, 1)

    def test_get_function_list(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        fix_tkinter_issues_virtualenv(fLOG=fLOG)
        funcs = get_function_list(src.tkinterquickhelper)
        assert isinstance(funcs, dict)
        assert len(funcs) > 0
        f = private_get_function("os.listdir")
        fLOG("**", f)


if __name__ == "__main__":
    unittest.main()
