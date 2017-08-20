"""A module containing functions related to search"""
import os
import curses
import logging

from . import util

SEARCH_STRING_JUMP_FORWARD = 'forward'
SEARCH_STRING_JUMP_BACKWARD = 'backward'
BBLAMEHST_PATH = os.path.join(os.path.expanduser('~'), '.bblamehst')
HISTORY_LIMIT = 50


def find_search_locs(scr_content, search_str):
    """find all the indexes of lines that contain the search string"""
    search_locs = []
    if search_str:
        for idx, line in enumerate(scr_content):
            if search_str in line.full_text():
                search_locs.append(idx)
            if idx == len(scr_content) - 1:
                break
    return search_locs


def re_create_hist_dir():
    """Unlinks the current hist dir if any, and re-create it.
    Called when something has gone wrong with the history file, either someone
    has changed the file permissions, ownership, etc. Just start fresh with a
    new file."""
    try:
        os.unlink(BBLAMEHST_PATH)
    except OSError as err:
        # If the  error is anything but file doesn't exist, then we have an
        # issue.
        if err.errno != 2:
            raise err
    # Essentially just "touch" the file to create it
    open(BBLAMEHST_PATH, 'a').close()


def read_search_history():
    """Load the stored search history from disk. File is .bblamehst.
    History is limited to 50 entries"""
    try:
        with open(BBLAMEHST_PATH, 'r') as bblamehst_file:
            return bblamehst_file.read().splitlines()
    # pylint: disable=bare-except
    except:
        re_create_hist_dir()
        return []


def write_search_history(history):
    """Write the stored search history to disk. File is ~/.bblamehst
    History is limited to 50 entries"""
    def write_to_hist_file():
        with open(BBLAMEHST_PATH, 'w') as bblamehst_file:
            for search_pattern in history:
                bblamehst_file.write(search_pattern + '\n')
    try:
        write_to_hist_file()
    # pylint: disable=bare-except
    except:
        re_create_hist_dir()
        try:
            write_to_hist_file()
        # pylint: disable=bare-except
        except:
            # Give up at this point, but don't kill the whole application.
            # Since this isn't a crucial feature.
            pass


def add_search_str_to_history(search_history, search_str):
    """Add the search_str to the search history to be written to disk.
    Ensuring to keep the history <= the history limit"""
    # search_history.append(search_str)
    search_history.insert(0, search_str)
    logging.info('search history: %s', search_history)
    return search_history[:HISTORY_LIMIT]


def append_string(txtbox, str_to_append):
    """Add string to the texteditpad textbox. This is not an append, will
    overwrite the existing text"""
    txtbox.text = [str_to_append]
    set_txtbox_cursor_pos(txtbox, 0, len(str_to_append))
    txtbox.redraw_vlines(txtbox.vptl, (0, 0))


def clear_search_txtbox(txtbox):
    """Clear the current text from the txtbox"""
    if len(''.join(txtbox.text)) > 0:
        txtbox.text = ['']
        set_txtbox_cursor_pos(txtbox, 0, 0)
        txtbox.redraw_vlines(txtbox.vptl, (0, 0))


def set_txtbox_cursor_pos(txtbox, x_pos, y_pos):
    """Set the cursor position of the texteditpad cursor"""
    txtbox.ppos = (x_pos, y_pos)  # physical position of the cursor
    txtbox.vpos = (x_pos, y_pos)  # virtual position of the cursor


def collect_search_string(txtbox):
    """Collect the search string from the user. Handling each character
    inputted into the txtbox, and handling the result
    """
    search_history = read_search_history()
    logging.info('SEARCH: history list: %s', search_history)
    history_iter = util.BidirectionalCycle(search_history, no_wrap=True)
    logging.info("SEARCH: history iter %s", history_iter)
    while True:
        char = txtbox.win.getch()
        if len(''.join(txtbox.text)) == 0:
            history_enabled = True
        # Enter key breaks out of the collection loop
        if char == curses.KEY_ENTER or char == ord('\n'):
            break
        # Handle backspace here if the textbox is empty, if so, exit the
        # collection loop
        elif char in [8, curses.KEY_BACKSPACE, curses.KEY_DC] and \
                len(''.join(txtbox.text)) == 0:
            return
        # Handle key up and down here if the textbox is empty, if so, cycle
        # through the past search history
        elif char in [curses.KEY_DOWN,
                      curses.KEY_UP] and history_iter and history_enabled:
            # clear_search_txtbox(txtbox)
            try:
                if char == curses.KEY_UP:
                    next_search = next(history_iter)
                else:
                    next_search = history_iter.prev()
            except StopIteration:
                # We've hit the end of the history, just return the current
                # item instead of advancing to the next or previous
                next_search = history_iter.curr()
            append_string(txtbox, next_search)
            logging.info('SEARCH: history next: %s', next_search)
        # Pass the key off to the textpad to handle from here
        else:
            history_enabled = False
            txtbox.do_command(char)

    search_str = ''.join(txtbox.text)
    # It's not helpful to add adjacent duplicates to search history, so only
    # add an item if it's unique compared to the last added item
    if not search_history or search_history[0] != search_str:
        search_history = add_search_str_to_history(search_history, search_str)
    write_search_history(search_history)

    return search_str
