#!/usr/bin/env python

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import logging

logger = logging.getLogger(__name__)

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, GObject
except ImportError:
    print("ERR: GTK not available")
    sys.exit(1)

from ..dstat import state, dfu

class InfoDialog(object):
    def __init__(self, parent, connect, signal='activate'):
        self.parent = parent
        connect.connect(signal, self.activate)

    def activate(self, object=None, data=None):
        self.dialog = Gtk.MessageDialog(self.parent, 0, Gtk.MessageType.INFO,
                                        Gtk.ButtonsType.OK, "DStat Info")
        self.dialog.format_secondary_text(
            "PCB Version: {}\n".format(state.dstat_version.base_version) + 
            "Firmware Version: {}".format(state.firmware_version)
        )
        
        self.dialog.connect('response', self.destroy)
        self.dialog.show()
        
    def destroy(self, object=None, data=None):
        self.dialog.destroy()
    