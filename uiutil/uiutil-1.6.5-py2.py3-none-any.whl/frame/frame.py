
import ttk

from ..mixin import AllMixIn


class BaseFrame(ttk.Frame,
                AllMixIn):

    def __init__(self,
                 parent,
                 grid_row=0,
                 grid_column=0,
                 grid_padx=5,
                 grid_pady=5,
                 *args,
                 **kwargs):

        self.parent = parent
        self._grid_row = grid_row
        self._grid_column = grid_column
        self._grid_padx = grid_padx
        self._grid_pady = grid_pady

        # Unfortunately everything Tkinter is written in Old-Style classes so it blows up if you use super!
        ttk.Frame.__init__(self, master=parent, **kwargs)
        AllMixIn.__init__(self, *args, **kwargs)
