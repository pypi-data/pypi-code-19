#!/usr/bin/python3
import importlib
import logging
import sys

import pyperclip
import urwid
from settings import Settings

import time

class TerminalCopyMachine:
    def __init__(self, switch_name, use_macro=False, toggle_chat=False, **cmd_args):
        self.choices = {}
        self.switch = None
        self.list_display = None

        # Currently pressed keys (like modifiers etc)
        self.toggle_chat = toggle_chat
        self.use_macro = use_macro

        if self.use_macro:
            global keyboard
            keyboard = importlib.import_module('keyboard')


        self._import_switch(switch_name)
        self.main_frame = self.menu()
        main = urwid.Padding(self.main_frame, left=2, right=2)
        self.main_loop = urwid.MainLoop(main, palette=[('reversed', 'standout', '')], input_filter=self.filter_input,
                                        unhandled_input=self.handle_input)

    def _import_switch(self, conf_name):
        conf_module = importlib.import_module("configurations.{}".format(conf_name))
        self.switch = conf_module.Switch()

    def tab(self, conf):
        body = [urwid.Text(conf.name), urwid.Divider()]
        for c in conf.ordered_choices:
            button = urwid.Button(conf.choices[c]['title'])
            urwid.connect_signal(button, 'click', self.item_chosen, c)
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))

        return urwid.ListBox(urwid.SimpleFocusListWalker(body))

    def menu(self):
        button_list = []
        for tab in self.switch.get_tabinfos():
            button = urwid.Button(str(tab.name))
            urwid.connect_signal(button, 'click', self.tab_chosen, str(tab.name))
            button_list.append(button)

        self.tab_chosen(None, self.switch.tabs[0].name)
        body = self.list_display

        return urwid.Frame(body, header=urwid.Pile([urwid.Columns(button_list), urwid.Divider()]))

    def item_chosen(self, button, choice):
        if self.choices[choice]['text'] is not None:
            pyperclip.copy(self.choices[choice]['text'])

    def tab_chosen(self, button, choice):
        if self.list_display is None:
            self.list_display = urwid.WidgetPlaceholder(urwid.Padding(self.tab(self.switch.get_tab(choice))))
        else:
            self.list_display.original_widget = urwid.Padding(self.tab(self.switch.get_tab(choice)))
            self.main_frame.focus_position = 'body'
        self.choices = self.switch.get_tab(choice).choices
        if self.use_macro:
            self.register_hotkeys(self.switch.hotkeys)

    def paste_text(self, combination, text):
        pyperclip.copy(text)
        keyboard.release(combination)
        time.sleep(0.5)
        if self.toggle_chat:
            keyboard.press_and_release('enter')
        keyboard.press('ctrl+v')
        time.sleep(0.1)
        keyboard.release('ctrl+v')
        if self.toggle_chat:
            keyboard.press_and_release('enter')

    def register_hotkeys(self, hotkeys):
        logging.info('list of hotkeys: {}'.format(hotkeys))
        for combination in reversed(list(hotkeys)):
            logging.info(combination)
            logging.info(hotkeys[combination])
            keyboard.add_hotkey(combination, self.paste_text, args=[combination, hotkeys[combination]])

    def filter_input(self, keys, raw):
        """
        urwid-input
        Adds fancy mouse wheel functionality to ListBox, thanks to https://github.com/tamasgal/km3pipe/
        """
        if len(keys) == 1:
            if keys[0] in Settings.keys['up']:
                keys = Settings.scroll_scaling['key-up']
            elif keys[0] in Settings.keys['down']:
                keys = Settings.scroll_scaling['key-down']
            elif len(keys[0]) == 4 and keys[0][0] == 'mouse press':
                if keys[0][1] == 4:
                    keys = Settings.scroll_scaling['wheel-up']
                elif keys[0][1] == 5:
                    keys = Settings.scroll_scaling['wheel-down']

        return keys

    @staticmethod
    def handle_input(value):
        if value in Settings.keys['escape']:
            raise urwid.ExitMainLoop

    @staticmethod
    def exit_program(button):
        raise urwid.ExitMainLoop()

    def run(self):
        self.main_loop.run()


if __name__ == '__main__':
    logging.basicConfig(filename='example.log', level=logging.DEBUG)
    try:
        TerminalCopyMachine(sys.argv[1]).run()
    except IndexError:
        TerminalCopyMachine('tripletrouble', use_macro=False).run()

