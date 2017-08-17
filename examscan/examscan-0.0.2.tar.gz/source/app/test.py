
# The next two lines are not necessary if you installed TkDnd
# in a proper place.
import os
os.environ['TKDND_LIBRARY'] = os.path.join(os.path.dirname(__file__), 'tkdnd2.8')

import Tkinter
from tkdnd import TkDND

root = Tkinter.Tk()

dnd = TkDND(root)

entry = Tkinter.Entry()
entry.pack()

def handle(event):
    event.widget.insert(0, event.data)

dnd.bindtarget(entry, handle, 'text/uri-list')

root.mainloop()

