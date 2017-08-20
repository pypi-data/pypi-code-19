"""Classes and utility functions related to git data and operations on it"""
import os
import re
import curses
import logging
from datetime import datetime
from collections import namedtuple

import sh

from .highlight import get_lexer, highlight_lines
from .util import Line, left_str_strip, BaseContent


class BadRevException(Exception):
    """Simple custom exception to make exception handling easier up the
    stack"""
    pass


class NoSuchRevException(Exception):
    """Simple custom exception to make exception handling easier up the
    stack"""
    pass


NUM_TAB_SPACES = 4
ABBREV_LEN = 8
# Git blame appears to show always n+1 characters of the sha, where n is
# the number of chars you actually asked for...
ABBREV_LEN_BLAME = ABBREV_LEN - 1
# Git color pair names
GIT_COLOR_OLD = curses.COLOR_RED
GIT_COLOR_NEW = curses.COLOR_GREEN
GIT_COLOR_FRAG = curses.COLOR_CYAN
GIT_COLOR_FUNC = curses.COLOR_BLUE
GIT_COLOR_SHOW = curses.COLOR_YELLOW
GIT_COLOR_META = curses.COLOR_MAGENTA


def get_head_rev(filename):
    """Get the revision pointed to by HEAD for <filename> specifically"""
    cmd = ['rev-list', '--abbrev=%d' % ABBREV_LEN, '--max-count=1',
           'HEAD', '--', filename]
    git = sh.git.bake(_cwd=os.getcwd())
    revlist = git(*cmd)
    if not revlist.splitlines():
        raise NoSuchRevException('No revlist for HEAD for file: %s \n'
                                 % filename)
    else:
        # return the firs 8 chars of the revision
        return revlist.splitlines()[-1][:8]


class GitLog(object):
    """A class to represent the git log.
    Essentially a hash mapped linked list. A git sha is the key to a gitlog
    object, which can then traverse to it's parent or ancestor, and so on"""

    # pylint: disable=too-few-public-methods
    class LogEntry(object):
        """A class object to represent an entry of the git log.
        Stores the sha and filename for that commit, and references to this
        commits parent and ancestor"""
        def __init__(self, sha, filename, desc, parent=None, ancestor=None):
            self.sha = sha
            self.filename = filename
            self.desc = desc
            self.parent = parent
            self.ancestor = ancestor

    def __init__(self, initial_filename):
        self._gitlog = {}
        git = sh.git.bake('--no-pager', _cwd=os.getcwd())
        initial_log = git.log('--no-color', '--abbrev=%d' % ABBREV_LEN,
                              '--follow', '--oneline', '--name-only', '--',
                              '%s' % initial_filename)
        logging.info('Preparing Git Log')
        previous_log_entry = None
        curr_log_entry = None
        # Fancy syntax to iterate two lines at a time
        for sha_and_desc, filename in zip(*[iter(initial_log.splitlines())]*2):
            logging.info('sha_and_desc: %s', sha_and_desc)
            sha = sha_and_desc.split()[0]
            desc = ' '.join(sha_and_desc.split()[1:])
            curr_log_entry = self.LogEntry(sha, filename, desc,
                                           ancestor=previous_log_entry)
            if previous_log_entry:
                previous_log_entry.parent = curr_log_entry
            else:
                # Keep a reference to the head and tail (see below). To be used
                # for the action which snaps bblame to the first or most recent
                # commit for a file
                self.head = curr_log_entry
            previous_log_entry = curr_log_entry

            self._gitlog[sha] = curr_log_entry

        if curr_log_entry:
            self.tail = curr_log_entry

    def __getitem__(self, item):
        return self._gitlog[item]

    def __str__(self):
        return self._gitlog.__str__()

    def __iter__(self):
        return self._gitlog.__iter__()

    def __len__(self):
        return self._gitlog.__len__()


PorcelainChunk = namedtuple('PorcelainChunk',
                            ['author', 'author_mail', 'author_tz',
                             'author_time', 'sha', 'content', 'filename',
                             'orig_line_no', 'final_line_no'])


LineMetaData = namedtuple('LineMetaData',
                          ['sha', 'filename', 'orig_line_no'])


class Blame(BaseContent):
    """A class to represent a blame.

    Attributes:
        git_sha - The SHA of the git commit being blamed if one
        filename - The name of the file we are blaming
        lines - The output of git blame by line in a default dict
        lexer - The syntax lexer used to highlight this blame
        lines_metadata - Extra info for each line (e.g. sha, filename, etc)
        max_filename_len - used to pad the blame output
        max_author_len - used to pad the blame output
        syntax_highlighting_enabled - whether syntax highlighting is enabled
                                      across the app
    """

    def __init__(self, filename, syntax_highlighting_enabled, git_sha=''):
        git = sh.git.bake('--no-pager', _cwd=os.getcwd())
        self.filename = filename
        self.lines_metadata = {}
        self.max_filename_len = 0
        self.max_author_len = 0
        self.syntax_highlighting_enabled = syntax_highlighting_enabled

        if git_sha:
            try:
                cmd = [git_sha, '--line-porcelain',
                       '--abbrev=%d' % ABBREV_LEN_BLAME, '--', filename]
                self.lines = self.buildlinesdict(
                    git.blame(*cmd).stdout.splitlines())
            except sh.ErrorReturnCode_128 as exc:
                stderr = exc.stderr.decode('utf-8')
                if "no such path" in stderr:
                    raise NoSuchRevException(stderr)
                if "bad revision" in stderr:
                    raise BadRevException(stderr)
                raise
            self.git_sha = git_sha
        else:
            self.git_sha = get_head_rev(filename)
            self.lines = self.buildlinesdict(git.blame(
                '--line-porcelain', '--abbrev=%d' % ABBREV_LEN_BLAME,
                filename).stdout.splitlines())

        # Run any setup from the super class
        super(Blame, self).__init__()

        # Clean up git we don't need it anymore
        del git

    def process_porcelain_blame(self, lines):
        """Process raw line-porcelain output into porcelain chunk objects"""
        ret_list = []
        start_idx = 0

        logging.info('Processing porcelain blame')

        for idx, line in enumerate(lines):
            line = line.decode('utf-8')
            logging.info('Looking at line: %s', line)
            if re.match(r'\t.*', line):
                logging.info('FOUND A TAB')
                # Line starts with tab, we've hit the end of a porcelain chunk
                chunk_lines = lines[start_idx:idx+1]
                ret_list.append(self.process_porcelain_chunk(chunk_lines))
                logging.info('porcelain lines: %s', lines[start_idx:idx])
                start_idx = idx + 1
                logging.info(ret_list[-1])

        logging.info('ret_list: %r', ret_list)
        return ret_list

    def process_porcelain_chunk(self, chunk_lines):
        """Process a single porcelain chunk into a named tuple"""
        header_line_tokens = chunk_lines[0].decode('UTF-8').split()
        if len(header_line_tokens) == 3:
            sha, orig_line_no, final_line_no = header_line_tokens
        elif len(header_line_tokens) == 4:
            (sha, orig_line_no,
             final_line_no, mystery_value) = header_line_tokens
        else:
            raise Exception('Header of porcelain chunk has unexpected format!')

        content = chunk_lines[-1][1:].decode('UTF-8')
        # Convert tabs to spaces, tabs were unpredictably expanding and
        # causing issues
        content = content.replace('\t', ' '*NUM_TAB_SPACES)
        metadata = chunk_lines[:-1]
        author = None
        author_mail = None
        author_tz = None
        author_time = None
        filename = None

        # Simple processing since the format is known
        for line in metadata:
            logging.info('processing chunk line: %s', line)
            line = line.decode('UTF-8')

            if not author and line.startswith('author '):
                author = left_str_strip(line, 'author ')
                logging.info('author: %s', author)
                continue

            if not author_tz and line.startswith('author-tz '):
                author_tz = left_str_strip(line, 'author-tz ')
                logging.info('author_tz: %s', author_tz)
                continue

            if not author_mail and line.startswith('author-mail '):
                author_mail = left_str_strip(line, 'author-mail ')
                logging.info('author_mail: %s', author_mail)
                continue

            if not author_time and line.startswith('author-time '):
                author_time = left_str_strip(line, 'author-time ')
                logging.info('author_time: %s', author_time)
                continue

            if not filename and line.startswith('filename '):
                filename = left_str_strip(line, 'filename ')
                continue

        if not all([author, author_tz, author_time, author_mail,
                    filename, orig_line_no, final_line_no]):
            logging.debug('author: %s, author_tz: %s, author_time: %s, '
                          'author_mail: %s, content: %s, filename: %s, '
                          'orig_line_no: %s, final_line_no: %s',
                          author, author_tz, author_time, author_mail,
                          content, filename, orig_line_no,
                          final_line_no)
            raise Exception('Couldn\'t extract all needed data from git blame')

        ret = PorcelainChunk(author=author, author_mail=author_mail,
                             content=content, author_tz=author_tz,
                             author_time=author_time, sha=sha,
                             orig_line_no=orig_line_no,
                             final_line_no=final_line_no,
                             filename=filename)

        if len(author) > self.max_author_len:
            self.max_author_len = len(author)
        if len(filename) > self.max_filename_len:
            self.max_filename_len = len(filename)

        return ret

    def buildlinesdict(self, lines):
        """Construct the dictionary that holds the lines for the Blame. See
        documentation in BaseContent for more details"""
        ret = self.gen_default_lines_dict()
        metadata_segment_txt = '%s %s (%s %s %s %s) '
        porcelain_chunks = self.process_porcelain_blame(lines)
        num_lines = len(porcelain_chunks)

        if self.syntax_highlighting_enabled:
            content_lines = [chunk.content for chunk in porcelain_chunks]
            logging.info('Content lines for blame before highlighting: %s',
                         content_lines)

            self.lexer = get_lexer(content_lines, self.filename)
            if self.lexer is None or 'text/plain' in self.lexer.mimetypes:
                # Can't determine a lexer, so just use normal highlight
                self.lexer = None
                highlighted_lines = [[(line, curses.A_NORMAL)]
                                     for line in content_lines]
            else:
                highlighted_lines = highlight_lines(content_lines, self.lexer)
                logging.info('Using %s lexer', self.lexer.name)
                logging.info('Highlighted lines for blame: %s',
                             highlighted_lines)

        for idx, porcelain_chunk in enumerate(porcelain_chunks):
            logging.info('Building line chunk %s, at idx: %s',
                         porcelain_chunk.content, idx)
            line = Line()
            _sha = porcelain_chunk.sha[:ABBREV_LEN_BLAME+1]
            _author = porcelain_chunk.author.ljust(self.max_author_len)
            _filename = porcelain_chunk.filename.ljust(self.max_filename_len)
            _line_no = porcelain_chunk.final_line_no.rjust(len(str(num_lines)))
            dtime = datetime.fromtimestamp(float(porcelain_chunk.author_time))
            _author_time = dtime.strftime('%Y-%m-%d %H:%M:%S')

            line.add_segment(metadata_segment_txt % (_sha, _filename, _author,
                                                     _author_time,
                                                     porcelain_chunk.author_tz,
                                                     _line_no), curses.A_DIM)

            if self.syntax_highlighting_enabled:
                highlighted_line = highlighted_lines[idx]
                logging.info('highlighted content: %s', highlighted_line)
                for string, syntax_attrs in highlighted_line:
                    line.add_segment(string, syntax_attrs=syntax_attrs)
            else:
                line.add_segment(porcelain_chunk.content)

            logging.info('bline segments:: %s', line.line_segments)
            ret[idx] = line

            # keep track of some of the most important metadata for each line
            line_meta = LineMetaData(sha=_sha,
                                     filename=porcelain_chunk.filename,
                                     orig_line_no=porcelain_chunk.orig_line_no)
            self.lines_metadata[idx] = line_meta

        return ret


class Show(BaseContent):
    """A class to represent a git show.

    Attributes:
        showobj - The function object returned by sh.git, contains attributes
                   like the return code of the command, the stdout, etc.
        git_sha - The SHA of the git commit being showed
    """
    def __init__(self, git_sha):
        git = sh.git.bake('--no-pager', _cwd=os.getcwd())
        showobj = git.show('--no-color', git_sha)
        self.git_sha = git_sha
        self.lines = self.buildlinesdict(showobj.stdout.splitlines())

        # Run any setup from the super class
        super(Show, self).__init__()

        # Clean up git and showobj we don't need it anymore
        del git
        del showobj

    def buildlinesdict(self, lines):
        """Construct the dictionary that holds the lines for the Show. See
        documentation in BaseContent for more details.
        Colourize the lines appropriately for the different types of Show lines
        """
        ret = self.gen_default_lines_dict()
        for idx, line in enumerate(lines):

            if isinstance(line, bytes):
                line = line.decode('UTF-8')

            # Check for the various git show colours
            # Commit header
            if line.startswith('commit'):
                ret[idx] = Line([line], curses.color_pair(GIT_COLOR_SHOW))

            # Meta information block
            elif line.startswith(('diff', '---', '+++', 'index', 'new file')):
                ret[idx] = Line([line], curses.color_pair(GIT_COLOR_META))

            # hunk/fragment header
            elif line.startswith('@@'):
                header_match = re.match(r'(@@ .* @@)(.*)', line)
                # should have two groups, who together are the same length as
                # the original line (to ensure we captured all the text)
                if (header_match and len(header_match.groups()) == 2
                        # pylint: disable=bad-builtin
                        and sum(map(len, header_match.groups())) == len(line)):

                    # Use two segments and paint them different colours
                    ret[idx] = Line([header_match.groups()[0]],
                                    curses.color_pair(GIT_COLOR_FRAG))
                    ret[idx].add_segment(header_match.groups()[1],
                                         curses.color_pair(GIT_COLOR_FUNC))

                # We couldn't properly parse the hunk header, just paint the
                # whole line the same colour
                else:
                    ret[idx] = Line([line], curses.color_pair(GIT_COLOR_FRAG))

            # added lines
            elif line.startswith('+'):
                ret[idx] = Line([line], curses.color_pair(GIT_COLOR_NEW))

            # removed lines
            elif line.startswith('-'):
                ret[idx] = Line([line], curses.color_pair(GIT_COLOR_OLD))

            # line with no interesting colours
            else:
                ret[idx] = Line([line])

        return ret
