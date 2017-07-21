
import os
from Tkconstants import HORIZONTAL, EW

import logging_helper
from frame.frame import BaseFrame
from window.child import ChildWindow

logging = logging_helper.setup_logging()


class LoadingFrame(BaseFrame):

    def __init__(self, wait_func=None, *args, **kwargs):

        self.wait_func = wait_func

        super(LoadingFrame, self).__init__(*args, **kwargs)

        self.progress = self.progressbar(length=280,
                                         orient=HORIZONTAL,
                                         mode=u'indeterminate',
                                         sticky=EW)
        self.progress.start()

        if self.wait_func is not None:
            self.after(ms=250, func=self.run)

    def run(self):
        self.wait_func()
        self.parent.master.destroy()


class LoadingWindow(ChildWindow):

    def __init__(self,
                 wait_func,
                 message=u'Loading...',
                 *args,
                 **kwargs):

        self.window_title = message
        self.wait_func = wait_func

        super(LoadingWindow, self).__init__(width=300,
                                            height=40 if os.name == u'nt' else 35,
                                            fixed=True,
                                            padding=u'0 0 0 0',
                                            *args,
                                            **kwargs)

    def _setup(self):
        self.overrideredirect(1)  # Setting this to 1 makes window borderless (plus no OS close button)

        self.config = LoadingFrame(parent=self._main_frame,
                                   wait_func=self.wait_func)
        self.config.grid(sticky=EW)


def start_loading(parent,
                  wait_func):

    loading = LoadingWindow(wait_func=wait_func,
                            parent_geometry=parent.winfo_toplevel().winfo_geometry())

    loading.transient(parent)
    loading.grab_set()
    parent.wait_window(loading)
