import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

import os
import re
import subprocess

class GtkPassWindow(Gtk.Window):
    
    def __init__(self):
        self.search_text = ''
        self.search_result_text = ''
        self.build_gui()
        self.build_data_structures()

    def build_gui(self):
        Gtk.Window.__init__(self, title='pass')
        self.set_border_width(10)
        self.set_default_size(300, -1)
        self.text_view = Gtk.Entry()
        self.text_view.set_editable(False)
        self.text_view.set_can_focus(False)
        self.text_entry = Gtk.Entry()
        self.text_entry.connect('key-release-event', self.on_key_release)
        self.text_entry.connect('activate', self.on_activate)
        self.text_entry.set_icon_from_icon_name(
                        Gtk.EntryIconPosition.PRIMARY,
                        'system-search-symbolic')
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.box.pack_start(self.text_view, True, True, 0)
        self.box.pack_start(self.text_entry, True, True, 0)
        self.add(self.box)
        self.text_entry.grab_focus()

    def build_data_structures(self):
        self.pass_path = os.path.expanduser('~/.password-store')
        self.pass_list = []
        self.pass_dict = {}
        for root, dirs, files in os.walk(self.pass_path):
            dirs[:] = [d for d in dirs if d[0] != '.']
            files[:] = [f for f in files if f[0] != '.']
            for file_ in files:
                gpg_path = os.path.join(root, file_)
                item_name = os.path.splitext(os.path.relpath(
                            gpg_path, self.pass_path))[0]
                self.pass_list.append(item_name)
                self.pass_dict[item_name] = gpg_path

    def fuzzy_find(self):
        suggestions = []
        pattern = '.*?'.join(map(re.escape, self.search_text))
        regex = re.compile(pattern, re.IGNORECASE)
        for item in self.pass_list:
            result = regex.search(item)
            if result:
                suggestions.append((len(result.group()), item))
        suggestions = sorted(suggestions, key=lambda x: x[0])
        return [item[1] for item in suggestions]

    def on_key_release(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()
        self.search_text = self.text_entry.get_text().strip()
        if self.search_text == '':
            self.search_result_text = None
        else:
            search_result = self.fuzzy_find()
            if search_result == []:
                self.search_result_text = None
            else:
                self.search_result_text = search_result[0]
        if self.search_result_text:
            self.text_view.set_text(self.search_result_text)
        else:
            self.text_view.set_text('')

    def on_button_release(self, widget, event):
        self.copy_to_clipboard()

    def on_activate(self, event):
        self.copy_to_clipboard()

    def copy_to_clipboard(self):
        if self.search_result_text:
            subprocess.call(['pass', '-c', self.search_result_text])
            self.text_entry.set_icon_from_icon_name(
                            Gtk.EntryIconPosition.SECONDARY,
                            'edit-paste-symbolic')


def main():
    win = GtkPassWindow()
    win.connect('delete-event', Gtk.main_quit)
    win.show_all()
    Gtk.main()
