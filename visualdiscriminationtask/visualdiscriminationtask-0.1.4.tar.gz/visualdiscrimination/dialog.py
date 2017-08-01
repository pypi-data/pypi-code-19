#!/usr/bin/env python
from tkinter import filedialog, Tk

def open_file_dialog():
    """
    Offers a GUI file prompt; requests a directory to store the data in
    """
    Tk().withdraw()  # we don't want a full GUI; remove root window
    config_dirname = filedialog.askdirectory()
    return config_dirname