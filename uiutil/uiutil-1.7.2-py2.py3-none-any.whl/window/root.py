
from Tkinter import Tk

from _base import BaseWindow


class RootWindow(BaseWindow,
                 Tk):

    def __init__(self,
                 *args,
                 **kwargs):

        Tk.__init__(self)
        super(RootWindow, self).__init__(*args, **kwargs)

        self.mainloop()
