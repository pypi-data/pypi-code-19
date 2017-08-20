"""Module that holds the mapping of key press to action.
Some actions are simple and the code needed runs here. Other actions involve
complex operations usually done in the screen object, and are just triggered by
actions.
The ActionTable class knows enough about each action (it's name, key, a short
description, the modes it applies to, etc) such that the help screen can be
generated entirely programatically."""

import curses
from curses import ascii as curses_ascii
import types
import logging

from . import modes
from .util import BaseContent


CURSES_KEY_TO_STR = {key_int: key_str[4:] for key_str, key_int in
                     list(vars(curses).items())
                     if key_str.startswith('KEY_')}
# Add mapping for escape
CURSES_KEY_TO_STR[27] = 'ESC'


# I don't love this class here, but seems silly to create a module for it and
# since the help screen is generated from Action class, there is already a fair
# amount of help code here.
class Help(BaseContent):
    """Class to represent help content.
    Basically just the base class"""
    def __init__(self, help_lines):
        self.lines = self.buildlinesdict(help_lines)
        # Run any setup from the super class
        super(Help, self).__init__()

    def buildlinesdict(self, help_lines):
        """No interesting processing/manipulation done to the lines of the
        help screen before being displayed"""
        return super(Help, self).buildlinesdict(help_lines)


class Action(object):
    """Object to represent a action the user can take in the bblame
    application"""
    def __init__(self, name, func, keys,
                 # NOTE: No default value to force the developer to think
                 # about which modes an action should be usable from, as this
                 # has led to a lot of bugs in the past.
                 action_modes,
                 desc='', show_in_help_msg=True):
        """Given inputs, validate they are at least of the right type and
        create a action table entry
        Attributes:
         name': name of action
         desc: short description of action, NOTE: this is shown in help page
         func: associated function to call when user enacts this action
         action_modes: The modes in which this action is functional
         show_in_help_msg: Toggle whether or not this action is in help page
        """
        # If no description was passed use the doc of the function
        if not desc:
            desc = func.__doc__
        assert isinstance(name, str)
        assert isinstance(desc, str)
        assert isinstance(func, types.MethodType)
        assert isinstance(action_modes, list)
        assert isinstance(keys, list)
        assert isinstance(show_in_help_msg, bool)

        self.name = name
        self.desc = desc
        self.func = func
        self.modes = action_modes
        self.show_in_help_msg = show_in_help_msg
        self.keys = keys

    def int_keys(self):
        """Return a list of this actions keys in integer/ascii form"""
        int_keys = []

        for key in self.keys:
            if isinstance(key, int):
                int_keys.append(key)
            elif isinstance(key, str):
                # convert char to int key code
                assert len(key) == 1, "Keys must be a single char!"
                int_keys.append(ord(key))
            else:
                raise Exception('Unexpected key type')

        return int_keys

    def str_keys(self):
        """Return a list of this actions keys in str form"""
        str_keys = []

        for key in self.keys:
            if isinstance(key, str):
                str_keys.append(key)
            elif isinstance(key, int):
                str_key = CURSES_KEY_TO_STR.get(key)
                if str_key:
                    str_keys.append(str_key)
            else:
                raise Exception('Unexpected key type')

        return str_keys


class ActionTable(object):
    """a class for accepting keys and performing actions"""
    def __init__(self, app_stdscr, scrobj):
        self.screen = scrobj
        self.app_stdscr = app_stdscr
        self._init_action_tables()

    # Not using self here, but I don't want this to be a staticmethod, since
    # that fails the method instance check inside Action
    # pylint: disable=no-self-use
    def quit_action(self):
        """Quit the application"""
        # For now just exit
        exit(0)

    def resize_action(self):
        """Resize the screens on a resize event"""
        logging.info('RESIZE EVENT')
        self.screen.resize_windows(self.app_stdscr)
        self.screen.redraw_screen()

    def move_up_action(self):
        """move the screen or visual select cursor up"""
        # if mode is visual, move line highlight
        if self._if_mode_visual():
            self.screen.move_cursor_up()
        # if mode is normal, move screen
        else:
            self.screen.move_scr_up()
        return True

    def move_down_action(self):
        """move the screen or visual select cursor down"""
        # if mode is visual, move line highlight
        if self._if_mode_visual():
            self.screen.move_cursor_down()
        # if mode is normal, move screen
        else:
            self.screen.move_scr_down()
        return True

    def help_action(self):
        """Display the help message"""
        if self._if_mode_help():
            self.screen.status_bar_toast('Already displaying help!')
        else:
            help_msg = self.generate_help()
            self.screen.display_help(Help(help_msg))

    def syntax_action(self):
        """Toggle syntax highlighting on or off. Showing or hiding syntax
        highlighting ONLY IF IT IS ENABLED."""
        screen = self.screen
        if not screen.syntax_highlighting_enabled:
            # Syntax highlighting is disabled entirely by user from cli
            screen.status_bar_toast('Syntax highlighting is disabled, cannot '
                                    'toggle')
            return

        # Toggle highlighting on or off
        screen.syntax_toggle = not screen.syntax_toggle
        logging.info('Syntax toggle: %s', screen.syntax_toggle)

        # Toast to the user the syntax lexer we're using for highlighting
        if screen.mode in [modes.MODE_NORMAL, modes.MODE_VISUAL]:
            lexer = screen.get_current_scr_content().lexer
            if not lexer:
                # Syntax highlighting is enabled but we couldn't determine a
                # lexer to use, either the file isn't formatted correctly,
                # it's just plain text, or pygments doesn't have a lexer for
                # this file type. Let the user know this, so they have some
                # explanation for why nothing happened after they ran the
                # syntax toggle action.
                screen.status_bar_toast('Could not determine file syntax, not '
                                        'highlighting')
                return
            else:
                # If toggling on syntax highlighting, toast to the user which
                # syntax lexer we're using
                if screen.syntax_toggle:
                    screen.status_bar_toast('Highlighting with %s syntax'
                                            % lexer.name)

    def escape_action(self):
        """Return to Normal mode"""
        if self.screen.mode in [modes.MODE_VISUAL]:
            self.screen.mode = modes.MODE_NORMAL
        elif self.screen.mode in [modes.MODE_SHOW, modes.MODE_HELP]:
            self.screen.restore_prev_content_and_state()

    def _if_mode_normal(self):
        """check if the screen obj is in NORMAL mode"""
        return self.screen.mode == modes.MODE_NORMAL

    def _if_mode_visual(self):
        """check if the screen obj is in VISUAL mode"""
        return self.screen.mode == modes.MODE_VISUAL

    def _if_mode_show(self):
        """check if the screen obj is in SHOW mode"""
        return self.screen.mode == modes.MODE_SHOW

    def _if_mode_help(self):
        """check if the screen obj is in HELP mode"""
        return self.screen.mode == modes.MODE_HELP

    def action_mode_warning(self, action):
        """Log and warn the user that the action they are trying to perform
        isn't available in the current mode they're in"""
        log_msg = ('Action "%s" not available in %s mode!'
                   % (action.name, self.screen.mode))
        logging.info(log_msg)
        self.screen.status_bar_toast(log_msg)

    def process_key(self, key):
        """Take a key and check if we have a corresponding action, if so call
        the action function, and log the keypress"""
        isascii = curses_ascii.isascii(key)
        ascii_key = chr(key) if isascii else None
        logging.info('KEY PRESSED (int, ascii), (%s, %s)', key, ascii_key)
        action = self.key_to_action.get(key, None)
        if action:
            logging.info('Associated action: %s', action.name)
            if self.screen.mode not in action.modes:
                self.action_mode_warning(action)
            else:
                logging.info('Calling action func: %s', action.name)
                return action.func()

        logging.info('Key not in action table')

    def generate_help(self):
        """Automagically generate a help document from the action descriptions
        in the action table"""
        help_lines = []
        help_lines.append('KEYS: ACTION - DESCRIPTION')
        help_lines.append('--------------------------')

        for action in self.actions:
            if action.show_in_help_msg:
                keys_str = ', '.join([_f for _f in action.str_keys() if _f])
                help_lines.append(' %s:   %s' % (keys_str, action.name))
                for desc_line in action.desc.splitlines():
                    help_lines.append('    %s' % (desc_line.strip()))
                help_lines.append('')

        return help_lines

    def _init_action_tables(self):
        """From a list of Action objects generate a dict that maps
        single keys to the action that they perform"""
        self.actions = [
            Action('Quit', self.quit_action,
                   ['q'], modes.ALL_MODES),
            Action('Screen Resize', self.resize_action,
                   [curses.KEY_RESIZE], modes.ALL_MODES,
                   show_in_help_msg=False),
            Action('Search', self.screen.get_search_string,
                   ['/'], modes.ALL_MODES_BUT_HELP,
                   'Search downward through the current blame or commit'),
            Action('Next Search Match', self.screen.jump_to_next_search_match,
                   ['n'], modes.ALL_MODES_BUT_HELP,
                   'Jump to the next search match (in the downward '
                   'direction)'),
            Action('Prev Search Match', self.screen.jump_to_prev_search_match,
                   ['N'], modes.ALL_MODES_BUT_HELP,
                   'Jump to the prev search match (in the upward direction)'),
            Action('Visual Select Mode', self.screen.init_vis_cursor,
                   ['v'], [modes.MODE_NORMAL],
                   'Enter visual select mode (only from normal mode)'),
            Action('Show/View Commit', self.screen.init_git_show,
                   ['o'], [modes.MODE_VISUAL],
                   'Show a commit selected by the visual mode cursor'),
            Action('Show/View file Commit', self.screen.init_git_show_file,
                   ['O'], modes.NORMAL_AND_VISUAL,
                   'Show the current revision commit'),
            Action('Normal Mode', self.escape_action,
                   [27], modes.ALL_MODES),
            Action('Drill Down', self.screen.add_blame_drill,
                   [10, curses.KEY_ENTER, 'd'], [modes.MODE_VISUAL],
                   'Drill down past the commit highlighted in visual mode. '
                   'Opens a new git blame'),
            Action('Parent blame', self.screen.add_blame_parent,
                   ['<', ','], modes.NORMAL_AND_VISUAL,
                   'Move to git blame of the parent of current commit \n'
                   '(i.e. traverse backwards through history, one commit at '
                   'a time)'),
            Action('Ancestor blame', self.screen.add_blame_ancestor,
                   ['>', '.'], modes.NORMAL_AND_VISUAL,
                   'Move to git blame of the ancestor of current commit \n'
                   '(i.e. traverse forwards through history, one commit at '
                   'a time)'),
            Action('Pop Back', self.screen.restore_prev_content_and_state,
                   [8, curses.KEY_BACKSPACE, curses.KEY_DC, 127, 'f'],
                   modes.ALL_MODES,
                   'Pop back to previous git object'),
            Action('Move Up', self.move_up_action,
                   ['k', curses.KEY_UP], modes.ALL_MODES,
                   show_in_help_msg=False),
            Action('Move Down', self.move_down_action,
                   ['j', curses.KEY_DOWN], modes.ALL_MODES,
                   show_in_help_msg=False),
            Action('Move Up Page', self.screen.move_scr_up_page,
                   [curses.KEY_PPAGE], modes.ALL_MODES,
                   'Move the screen up one page',
                   show_in_help_msg=False),
            Action('Move Down Page', self.screen.move_scr_down_page,
                   [curses.KEY_NPAGE], modes.ALL_MODES,
                   'Move the screen down one page',
                   show_in_help_msg=False),
            Action('Move Right Page', self.screen.move_scr_right_nchars,
                   [curses.KEY_RIGHT], modes.ALL_MODES,
                   'Move the screen half a page to the right',
                   show_in_help_msg=False),
            Action('Move Left Page', self.screen.move_scr_left_nchars,
                   [curses.KEY_LEFT], modes.ALL_MODES,
                   'Move the screen half a page to the left',
                   show_in_help_msg=False),
            Action('Jump to Top', self.screen.move_scr_to_top,
                   ['g', curses.KEY_HOME], modes.ALL_MODES,
                   'Jump to the top of the screen'),
            Action('Jump to Bottom', self.screen.move_scr_to_bottom,
                   ['G', curses.KEY_END], modes.ALL_MODES,
                   'Jump to the bottom of the screen'),
            Action('Help', self.help_action,
                   ['h'], modes.ALL_MODES),
            Action('Toggle Syntax Highlight', self.syntax_action,
                   ['s'], modes.ALL_MODES),
            Action('Jump to HEAD', self.screen.add_head_blame,
                   ['H'], modes.NORMAL_AND_VISUAL,
                   'Jump to a blame of the most recent commit for the file'),
            Action('Jump to TAIL', self.screen.add_tail_blame,
                   ['T'], modes.NORMAL_AND_VISUAL,
                   'Jump to a blame of the first commit for the file'),
        ]

        # Create a mapping of each single key (as its int keycode) to
        # the action, to make single key lookups easier in main loop
        self.key_to_action = {}
        for action in self.actions:
            for key in action.int_keys():
                if key in self.key_to_action:
                    raise Exception('Duplicate action key! %s mapped to %s '
                                    'and %s' % (key, action.name,
                                                self.key_to_action[key].name))
                self.key_to_action[key] = action
