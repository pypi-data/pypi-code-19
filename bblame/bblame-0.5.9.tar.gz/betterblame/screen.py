"""Screen object reacts to user input updating the curses screen"""
import curses
import logging

import texteditpad

from . import modes
from . import search
from . import git
from . import contentstack

from .util import BidirectionalCycle


class BadModeException(Exception):
    """Simple exception to make exception handling easier up the stack"""
    pass


class UserError(Exception):
    """Simple exception to make exception handling easier up the stack"""
    pass


class CurrentPos(object):
    """A small data class to represent the positional data of a bblame screen.
    Attributes:
        cursor_line - The current line the cursor is on. Relative to the
                      visible screen, E.g.: cursor_line is always between
                      0 and screen height
        current_line - The current line of content, zero indexed from the top.
                       E.g. After freshly opening a blame, current_line is 0,
                            after scrolling down 5 lines, current_line is 4
        current_width - similar to current
    """
    def __init__(self, cursor_line, current_line, current_width):
        self.cursor_line = cursor_line
        self.current_line = current_line
        self.current_width = current_width

    def incr_cursor_line(self, num_lines=1):
        """Increment cursor line by <num_lines>"""
        self.cursor_line = self.cursor_line + num_lines

    def incr_current_line(self, num_lines=1):
        """Increment current line by <num_lines>"""
        self.current_line = self.current_line + num_lines

    def incr_current_width(self, num_cols=1):
        """Increment current width by <num_cols>"""
        self.current_width = self.current_width + num_cols

    def decr_cursor_line(self, num_lines=1):
        """Decrements cursor line by <num_lines>"""
        self.cursor_line = self.cursor_line - num_lines

    def decr_current_line(self, num_lines=1):
        """Decrements current line by <num_lines>"""
        self.current_line = self.current_line - num_lines

    def decr_current_width(self, num_cols=1):
        """Decrements current width by <num_cols>"""
        self.current_width = self.current_width - num_cols


class Screen(object):
    """The main class that bridges between the curses screen object and one
    or more blame or git show objects. Containing functions that are triggered
    by user interaction with the application which modify and/or read
    screen/git state.

    Attributes:
        stdscr - The curses screen object
        search_locs_iter - bidirectional iterator of the indexes to lines that
                           contain the current search pattern
        content_stack - A stack to keep track of git blame/show objects as
                        you browse file commit history and show commits.
        mode - The current mode bblame is in, see modes.py for more details
        search_str - current search string, if any.
    """

    def __init__(self, stdscr, filename, revision,
                 syntax_highlighting_enabled):
        self.current_pos = CurrentPos(0, 0, 0)
        self.search_locs_iter = None
        self.status_bar_next_msg = ''
        self.mode = modes.MODE_NORMAL
        self.content_stack = contentstack.ContentStack()
        self.gitlog = git.GitLog(filename)
        self.search_str = None
        self.syntax_highlighting_enabled = syntax_highlighting_enabled
        self.syntax_toggle = True  # enabled by default

        self.resize_windows(stdscr)  # prepares the subwindows
        self.set_status_bar_next_msg('')
        self._add_content_to_stack(git.Blame(filename,
                                             syntax_highlighting_enabled,
                                             revision[:git.ABBREV_LEN]))

    @staticmethod
    def setup_screen(scr):
        """setup screens
        set scrollingok and idlok for scrolling)
        set keypad for use of arrow keys
        """
        scr.scrollok(1)
        scr.idlok(1)
        scr.keypad(True)

    def resize_windows(self, app_scr):
        """Partition stdscr into properly sized subwindows"""
        height, width = app_scr.getmaxyx()
        self.stdscr = app_scr.derwin(height-1, width, 0, 0)
        self.status_bar = app_scr.derwin(1, width, height-1, 0)
        self.setup_screen(self.stdscr)
        self.setup_screen(self.status_bar)
        self.setup_screen(app_scr)

    def erase_status_bar(self):
        """Erase the screen"""
        self.status_bar.erase()

    def refresh_status_bar(self):
        """Refresh the statusbar"""
        self.status_bar.refresh()

    def getch(self, nodelay=False):
        """wait for char with delay or not"""
        self.stdscr.nodelay(nodelay)
        char = self.stdscr.getch()
        self.stdscr.nodelay(False)
        return char

    def check_for_escape(self, char):
        """Check if the escape key was pressed, which is tricky as the Alt
        key combos also use escape"""
        if char == 27:
            # At this point we don't know if it was ESC or an ALT key combo
            # Grab another key to see if it was an ALT combo
            next_char = self.getch(nodelay=True)
            esc = False
            if next_char == -1:
                # Escape was pressed
                esc = True
            # NOTE: Don't care about ALT right now so just drop it on the floor
            #       if it was.
            return esc

    def _get_max_yx(self):
        """return the max width and height of the screen"""
        return self.stdscr.getmaxyx()

    def _get_visible_content_len(self):
        """Get the length of visible content, I.e. the number of lines of
        blame or git show that are visible to the user"""
        screen_h, screen_w = self._get_max_yx()
        scr_content = self.get_current_scr_content()
        return min(len(scr_content) - self.current_pos.current_line, screen_h)

    def add_head_blame(self):
        """Add blame for the most recent commit of this file"""
        self._add_blame(self.gitlog.head)

    def add_tail_blame(self):
        """Add blame for the first commit of this file"""
        self._add_blame(self.gitlog.tail)

    def add_blame_parent(self):
        """Add blame of the parent of the current rev to the content stack"""
        curr_rev = self.get_current_scr_content().git_sha
        git_log_entry = self.gitlog[curr_rev]
        self._add_blame(git_log_entry.parent)

    def add_blame_ancestor(self):
        """Add blame of the ancestor of the current rev to the content stack"""
        curr_rev = self.get_current_scr_content().git_sha
        git_log_entry = self.gitlog[curr_rev]
        self._add_blame(git_log_entry.ancestor)

    def add_blame_drill(self):
        """Add a blame to the content stack for the revision under
        the cursor"""
        _, line_meta = self._get_cursor_line(include_meta=True)
        rev_to_drill = line_meta.sha
        if rev_to_drill == '0'*len(rev_to_drill):
            # This is likely a non-committed change. The parent of a
            # non-committed change is HEAD of the file
            head_sha = self.get_current_scr_content().git_sha
            git_log_entry = self.gitlog[head_sha]
            self._add_blame(git_log_entry.parent)
        elif rev_to_drill.startswith('^'):
            # This is a boundary commit, can't drill past this
            raise UserError('Can\'t drill past boundary commit, no parent')
        else:
            git_log_entry = self.gitlog[rev_to_drill]
            self._add_blame(git_log_entry.parent)

    def _add_blame(self, git_log_entry):
        """Add a blame to the content stack. Takes the file we're blaming and
        a function that when called returns the revision of the file we're
        blaming"""
        try:
            if git_log_entry is None:
                logging.warning('YOU HAVE REACHED THE BOTTOM OF THE WELL!')
                current_rev = self.get_current_scr_content().git_sha
                raise UserError('Error: No commit before %s' % current_rev)
            filename = git_log_entry.filename
            revision = git_log_entry.sha
            newblame = git.Blame(filename, self.syntax_highlighting_enabled,
                                 '%s' % revision)
        except git.BadRevException:
            logging.warning('BAD REV SELECTED! %s', revision)
            raise UserError('Error: bad revision (%s) selected', revision)
        self._add_content_to_stack(newblame)
        self.update_search_locs()
        self.mode = modes.MODE_NORMAL

    def get_current_scr_content(self):
        """return the current screen content"""
        stackframe = self.content_stack.peek()
        return stackframe.content

    def _add_content_to_stack(self, content):
        """Add content to the content_stack, along with the current state
        needed to restore the screen after we remove it"""
        self.content_stack.add(content, self.current_pos.current_line,
                               self.current_pos.current_width,
                               self.current_pos.cursor_line, self.mode)

    def restore_prev_content_and_state(self):
        """Delete the current frame of the content stack, restore the
        snapshot of the previous screen state it stored"""
        try:
            stackframe = self.content_stack.pop()
        except IndexError:
            raise UserError('No content to pop')

        self.current_pos.current_line = stackframe.last_current_line
        self.current_pos.current_width = stackframe.last_current_width
        self.current_pos.cursor_line = stackframe.last_cursor_line
        self.mode = stackframe.last_mode

        self.update_search_locs()

    def display_help(self, help_obj):
        """Display help"""
        self._add_content_to_stack(help_obj)
        self.mode = modes.MODE_HELP

    def _get_line(self, line, include_meta=False):
        """Return the content at index <line> from the current content being
        displayed and the attributes of that line"""
        scr_content = self.get_current_scr_content()
        if include_meta:
            meta_line = scr_content.lines_metadata[line]
            return (scr_content[line], meta_line)
        return scr_content[line]

    def _get_cursor_line(self, include_meta=False):
        """Return the line that the cursory is on. If <include_meta>
        then also return the meta_data for the line, most commonly this is used
        to get the git sha for the line"""
        cursline_2_bline = (self.current_pos.cursor_line +
                            self.current_pos.current_line - 1)
        return self._get_line(cursline_2_bline, include_meta=include_meta)

    def set_status_bar_next_msg(self, content,
                                attributes=curses.A_DIM | curses.A_STANDOUT):
        """Set a message to be displayed in the status bar on the next screen
        refresh. Returns a tuple with the message content and any
        attributes"""
        self.status_bar_next_msg = (content, attributes)

    def status_bar_toast(self, content):
        """Set a message to be displayed in the status bar on the next screen
        refresh with bold attribute"""
        self.status_bar_next_msg = (content, curses.A_BOLD | curses.A_STANDOUT)

    def get_status_bar_content(self):
        """Return content to be displayed in the status bar. A standard
        template for each mode will be displayed unless an explicit status
        bar messages was set to be displayed"""
        scr_content = self.get_current_scr_content()
        height, width = self._get_max_yx()
        ret_msg = ''
        ret_attrs = curses.A_DIM | curses.A_STANDOUT

        if self.status_bar_next_msg[0]:
            ret_msg, ret_attrs = self.status_bar_next_msg
            self.set_status_bar_next_msg("")
        elif self.mode == modes.MODE_HELP:
            ret_msg = 'Help'
        else:
            git_sha = scr_content.git_sha
            if self.mode == modes.MODE_SHOW:
                ret_msg = '%s: %s' % ('show', git_sha)
            else:
                filename = scr_content.filename
                ret_msg = '%s: %s (%s)' % ('blame', filename, git_sha)
        return ret_msg, ret_attrs

    def _draw_status_bar(self):
        """Fetch the correct content to be displayed in the status bar and
        draw it in the status bar window."""
        content, attributes = self.get_status_bar_content()
        _, width = self._get_max_yx()
        content.ljust(width-1)
        # If the message is too long for the width of the screen, truncate it
        # and add an ellipses to indicate we've done so.
        if len(content) > width - 1:
            content = content[:width-4] + '...'

        self.erase_status_bar()
        self.status_bar.addstr(content[:width-1], attributes)
        self.refresh_status_bar()

    def init_git_show_file(self):
        """Setup for a git show for the file commit"""
        git_sha = self.get_current_scr_content().git_sha
        self.init_git_show(git_sha)

    def init_git_show(self, rev_to_show=None):
        """Setup for a git show"""
        _, line_meta = self._get_cursor_line(include_meta=True)
        rev = rev_to_show if rev_to_show else line_meta.sha
        show = git.Show(rev)
        self._add_content_to_stack(show)
        self.mode = modes.MODE_SHOW
        # Snap to top of git show
        self.current_pos.current_line = 0
        self.current_pos.current_width = 0
        self.update_search_locs()

    def get_search_string(self):
        """Get search string using texteditpad and some trickery"""
        # Create a subwindow in the statusbar to contain the single line
        # Textbox editor
        screen_h, screen_w = self._get_max_yx()
        # Create massive window to avoid hitting max width
        temp_search_win = curses.newwin(1, 900, screen_h, 1)
        txtbox = texteditpad.Textbox(temp_search_win, insert_mode=True)
        # Clear the status bar of status indicators, and print the search
        # string entry '/'
        self.erase_status_bar()
        self.status_bar.addstr(0, 0, '/')
        self.refresh_status_bar()
        # Enable the cursor and begin excepting text until the user hits return
        curses.curs_set(1)
        self.search_str = search.collect_search_string(txtbox)
        curses.curs_set(0)
        logging.info('SEARCH: search string: %s~', self.search_str)
        if not self.search_str:
            # Don't update anything since it will raise a user toast since no
            # matches will be found for the search string
            logging.info('SEARCH: no search string')
            return
        self.update_search_locs()
        self.jump_to_next_search_match()

    def jump_to_next_search_match(self):
        """Jump to the next search match"""
        self._jump_to_search_match_helper(search.SEARCH_STRING_JUMP_FORWARD)

    def jump_to_prev_search_match(self):
        """Jump to the previous search match"""
        self._jump_to_search_match_helper(search.SEARCH_STRING_JUMP_BACKWARD)

    def _jump_to_search_match_helper(self, direction):
        """Jump to next search match in <direction>"""
        if self.search_locs_iter is not None:
            try:
                if direction == search.SEARCH_STRING_JUMP_FORWARD:
                    self.current_pos.current_line = next(self.search_locs_iter)
                elif direction == search.SEARCH_STRING_JUMP_BACKWARD:
                    self.current_pos.current_line = \
                            self.search_locs_iter.prev()
                else:
                    raise Exception('Unknown search direction (%s) passed',
                                    direction)
                # Kick the user back to Normal/show mode when searching
                if self.mode == modes.MODE_VISUAL:
                    self.mode = modes.MODE_NORMAL
            except StopIteration:
                self.status_bar_toast('Error: Pattern not found')
        else:
            logging.info('No search pattern entered')

    def init_line_arg(self, content_line):
        """Setup the screen given the provided <content_line> from the user,
        passed from the command line.
        This is roughly:
            - centre the screen on that line if possible (stopping at top or
              bottom of content).
            - enable visual mode (placing the cursor on the location of the
              screen that is over overtop of <content_line>)."""
        screen_h, screen_w = self._get_max_yx()
        screen_loc_of_line = self._center_screen_on_line(content_line)
        self.init_vis_cursor(screen_loc_of_line)

    def init_vis_cursor(self, cursor_line=None):
        """init visual select cursor mode.
        Move to the correct mode and initialize the cursor to a either
        the provided line <cursor_line>, the position of the current search
        (if one exists and it's located in the current screen view) or the
        default (in the middle of the visible content)"""
        self.mode = modes.MODE_VISUAL
        screen_h, screen_w = self._get_max_yx()

        def current_search_line():
            """Turn search location into a one-based index content line"""
            return self.search_locs_iter.curr() + 1

        if cursor_line:
            self.current_pos.cursor_line = cursor_line
        # If we have a search and the current search hit is anywhere in the
        # viewable area
        elif (self.search_locs_iter and
              self.content_line_to_screen_line(current_search_line())):
            self.current_pos.cursor_line = self.content_line_to_screen_line(
                current_search_line())
        else:
            # If our blame has less lines than height then we want to init
            # the cursor to the middle of the blame content not into the middle
            # of the screen which could be off of the edge of file content.
            self.current_pos.cursor_line = self._get_visible_content_len()//2

    def content_line_to_screen_line(self, content_line):
        """Convert a content line (e.g. Line 4356 of a file/blame) and return
        the line on the viewable screen that <content_line> is on (e.g. screen
        line 6, i.e. six lines from the top of the screen the user sees).
        Returns None if <content_line> is not in the viewable area"""
        scrn_content_len = self._get_visible_content_len()
        current_line = self.current_pos.current_line
        if current_line < content_line <= current_line + scrn_content_len:
            return content_line - current_line

    def _center_screen_on_line(self, line):
        """Centers the screen around <line> of the blame as best as possible.
        Returns the location on the viewable screen space, where the line we
        wanted to center on ended up. In most cases this will indeed be the
        center (height/2) but may be elsewhere if we've reached the end of the
        git blame"""
        screen_h, screen_w = self._get_max_yx()
        scrn_content_len = len(self.get_current_scr_content())
        if line < screen_h//2:
            # Centering the screen at a line which would leave less than half
            # a screen height worth of content above wouldn't leave us with
            # enough content to fill the screen, so cap it at 0
            self.current_pos.current_line = 0
        elif line > (scrn_content_len - screen_h//2 - 1):
            # Same as above but we'd run off the bottom of the content, cap
            # things such that we have at least one screens worth of content
            # to display.
            self.current_pos.current_line = scrn_content_len - screen_h
        else:
            self.current_pos.current_line = line - screen_h//2
        return max(1, min(line - self.current_pos.current_line, screen_h))

    def _re_center_screen(self):
        """Called to recenter the screen.
        Redrawing the screen after drilling into a blame or popping back may
        leave all or part of the screen outside of the content, so recenter
        the screen on the new/changed content"""
        scrn_content = self.get_current_scr_content()
        screen_h, screen_w = self._get_max_yx()
        # recenter the screen if we're out of the content
        if self.current_pos.current_line > len(scrn_content):
            if len(scrn_content) < screen_h//2:
                self.current_pos.current_line = 0
            else:
                self.current_pos.current_line = len(scrn_content) - screen_h//2
        self._re_center_cursor()

    def _re_center_cursor(self):
        """Recenter the visual cursor"""
        screen_h, screen_w = self._get_max_yx()
        # recenter the visual mode cursor if it's outside the content
        if self.current_pos.cursor_line > self._get_visible_content_len():
            self.current_pos.cursor_line = self._get_visible_content_len()//2

    def _highlight_for_vis_cursor(self, content_index):
        """determines whether the current line should be highlighted for
        visual mode cursor"""
        # Pylint doesn't see both halves of the and as one. (no need for '\'
        # inside parens either)
        # pylint: disable=pointless-statement
        if (self.mode == modes.MODE_VISUAL and
                content_index == (self.current_pos.cursor_line - 1)):
            return True
        else:
            False

    def update_search_locs(self):
        """Creates a bi-directional iterator of all lines that contain the
        search pattern."""
        scr_content = self.get_current_scr_content()
        _search_locs = search.find_search_locs(scr_content, self.search_str)
        self.search_locs_iter = BidirectionalCycle(_search_locs)
        logging.info('SEARCH: Done updating search locs')

    def _draw_mapped_tokens(self, mapped_tokens, current_index):
        # TODO: possibly remove this
        """Draw line that is a list of tokens for search.
        This process is novel because the tokens have different curses attrs,
        so they must be added to the scr in pieces, and we also must be
        careful to stay within the current screen y position and width"""
        screen_h, screen_w = self._get_max_yx()
        curr_x_pos = start_pos = 0
        for token_str, highlight_for_search, token_attrs in mapped_tokens:
            token_len = len(token_str)
            if curr_x_pos == 0:
                # Until we've started printing the line check how much, if
                # any, of the current token fits in the screen width, it may
                # need to be clipped
                len_before_begin = ((start_pos + token_len) -
                                    self.current_pos.current_width)
                if len_before_begin < 0:
                    # Line not yet in the current width, (I.e. The user has
                    # shifted the screen over to the right, and the token we're
                    # currently processing doesn't fall in the viewable area
                    start_pos += token_len
                    continue
                # clip the token, as only part of it is in the viewable area
                token_str = token_str[token_len-len_before_begin:]
                token_len = len(token_str)
            # Check if the token will go past the width of the screen
            len_past_end = (curr_x_pos + token_len) - screen_w + 1
            if len_past_end > 0:
                # line would be longer than screen width, so trim
                token_str = token_str[0:-len_past_end]
            # If the current visual cursor line contains a search match, then
            # invert the highlight of the match so it still stands out
            if self._highlight_for_vis_cursor(current_index):
                highlight_for_search = not highlight_for_search
            if highlight_for_search:
                self.stdscr.addstr(current_index, curr_x_pos,
                                   token_str.encode('utf-8'),
                                   curses.A_STANDOUT | token_attrs)
            else:
                self.stdscr.addstr(current_index, curr_x_pos,
                                   token_str.encode('utf-8'), token_attrs)
            # Increment the x position by the length of the token we've added
            curr_x_pos += token_len
            if len_past_end > 0:
                break

    def redraw_screen(self):
        """Clear and redraw the screen, print each line and be sure to
        highlight the cursor line if we are in visual mode"""
        self._re_center_screen()
        screen_h, screen_w = self._get_max_yx()
        # <line_idx> is the index to the actual line of text from the file
        # that's being printed to the screen at line <scr_idx>. <scr_idx> is
        # always between 0 and height of the screen
        curr_line = self.current_pos.current_line
        curr_width = self.current_pos.current_width
        for scr_idx, line_idx in enumerate(range(curr_line,
                                                 curr_line + screen_h)):
            line = self._get_line(line_idx)
            # pylint for some reason can't see that line is a Line object and
            # not just a tuple
            # pylint: disable=no-member
            logging.info('drawing line: %s', line.line_segments)
            if self.search_locs_iter and line_idx in self.search_locs_iter:
                # This line contains at least one instance of the search string
                if self._highlight_for_vis_cursor(scr_idx):
                    line = line.highlight_str(self.search_str, None)
                else:
                    line = line.highlight_str(self.search_str,
                                              curses.A_STANDOUT)
                logging.info('highlighted line: %s', line.line_segments)
            # Only print as much of the line that will fit in the screen width
            logging.info('line: %s', str(line.full_text().encode('utf-8')))
            width_limited_line = line.get_sub_line(curr_width,
                                                   curr_width+screen_w-1)
            logging.info('len of new sub line: %d, width: %d',
                         len(width_limited_line), curr_width)

            num_chars_so_far = 0
            logging.info('Printing full line: %s',
                         width_limited_line.full_text())
            for segment in width_limited_line:
                logging.info('printing segment: %s, with attr %s and syntax %s'
                             ', on screen line: %s',
                             segment.text, segment.attributes,
                             segment.syntax_attrs, scr_idx)
                high_for_vis = self._highlight_for_vis_cursor(scr_idx)
                if high_for_vis and segment.text != self.search_str:
                    self.stdscr.addstr(scr_idx, num_chars_so_far,
                                       segment.text.encode('utf-8'),
                                       curses.A_STANDOUT | segment.attributes)
                else:
                    if self.syntax_toggle and segment.syntax_attrs:
                        curses_attrs = curses.color_pair(segment.syntax_attrs)
                        logging.info('syntax highlighting!')
                    else:
                        # If not using syntax highlighting just use the default
                        # curses attribute for the segment (dim, standout,
                        # normal, etc)
                        curses_attrs = segment.attributes
                        logging.info('NO syntax highlighting!')

                    logging.info('Segment attrs: %s', curses_attrs)
                    self.stdscr.addstr(scr_idx, num_chars_so_far,
                                       segment.text.encode('utf-8'),
                                       curses_attrs)

                num_chars_so_far += len(segment.text)

        self._draw_status_bar()

    def move_scr_down_page(self):
        """Move down by a page or less if there isn't a page full of content
        left"""
        scr_content = self.get_current_scr_content()
        screen_h, screen_w = self._get_max_yx()
        len_left = len(scr_content) - self.current_pos.current_line - screen_h
        if (len_left) > 0:
            page_size = min(len_left, screen_h)
            self.current_pos.incr_current_line(page_size)

    def move_scr_up_page(self):
        """move up by a page or less if there isn't a page full of content
        left"""
        screen_h, screen_w = self._get_max_yx()
        if self.current_pos.current_line > 0:
            page_size = min(screen_h, self.current_pos.current_line)
            self.current_pos.decr_current_line(page_size)

    def move_scr_right_nchars(self, nchars=8):
        """Move screen to the right by nchars"""
        screen_h, screen_w = self._get_max_yx()
        self.current_pos.incr_current_width(nchars)

    def move_scr_left_nchars(self, nchars=8):
        """Move screen to the left by nchars"""
        if self.current_pos.current_width > 0:
            self.current_pos.decr_current_width(nchars)

    def move_scr_down(self):
        """Move the screen down one line if we haven't reached the bottom yet
        """
        logging.info('MOVE_SCR_DOWN')
        scr_content = self.get_current_scr_content()
        screen_h, screen_w = self._get_max_yx()
        if (len(scr_content) - self.current_pos.current_line - screen_h) > 0:
            self.current_pos.incr_current_line()

    def move_scr_to_top(self):
        """Snap screen to top of content"""
        self.current_pos.current_line = 0

    def move_scr_to_bottom(self):
        """Snap screen to bottom of content"""
        scr_content = self.get_current_scr_content()
        screen_h, screen_w = self._get_max_yx()
        self.current_pos.current_line = len(scr_content) - screen_h

    def move_scr_up(self):
        """Move the screen up one lines if we haven't reached the top yet"""
        if self.current_pos.current_line > 0:
            self.current_pos.decr_current_line()

    def move_cursor_down(self):
        """Move the highlighted cursor line down by one line"""
        visable_content_len = self._get_visible_content_len()
        if self.current_pos.cursor_line <= visable_content_len:
            if self.current_pos.cursor_line == visable_content_len:
                # highlight is at the bottom of the screen
                self.move_scr_down()
            else:
                self.current_pos.incr_cursor_line()

    def move_cursor_up(self):
        """Move the highlighted cursor line up by one line"""
        if self.current_pos.cursor_line > 0:
            if self.current_pos.cursor_line == 1:
                # highlight is at the top of the screen
                self.move_scr_up()
            else:
                self.current_pos.decr_cursor_line()

    def log_state(self):
        """print some state to a log file"""
        content = self.get_current_scr_content()
        screen_h, screen_w = self._get_max_yx()
        logging.info('Content stack len: %s', len(self.content_stack))
        logging.info('Mode: %s', self.mode)
        logging.info('Screen height: %s', screen_h)
        logging.info('Screen width: %s', screen_w)
        logging.info('Current line: %s', self.current_pos.current_line)
        logging.info('Current width: %s', self.current_pos.current_width)
        logging.info('Cursor line: %s', self.current_pos.cursor_line)
        if self.search_locs_iter:
            logging.info('Current search line: %s',
                         self.search_locs_iter.curr())
        logging.info('Length of file: %s', len(content))
        logging.info('Length of file exposed: %d',
                     self._get_visible_content_len())
        logging.info('length of file - currline %s',
                     (len(content) - self.current_pos.current_line))
        logging.info('range: %s\n',
                     str(range(self.current_pos.current_line,
                               self.current_pos.current_line + screen_h)))
