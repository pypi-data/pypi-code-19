"""Utility functions and objects"""
import logging
import curses
import re
import gc
import zlib

from collections import namedtuple
from abc import ABCMeta, abstractmethod
from six import string_types
from collections import defaultdict

DEFAULT_CURSES_ATTR = curses.A_NORMAL


def substring_split(start, end, string):
    """Split string at start:end, returning all three substrings (beginning,
    middle, end) if available"""
    # print('substring_split, start: %d, end: %d' % (start, end))
    return string[:start], string[start:end], string[end:]


def left_str_strip(string, str_to_strip):
    """Strips whole string <str_to_strip> from <string> from the left side.
    Distinct from lstrip, since the latter strips all chars, in any order, from
    the string"""
    return string[len(str_to_strip):]


class Line(object):
    """A class to represent each line of the git object being shown (blame,
    show, etc)
    """

    # Definition of the segment tuple
    Segment = namedtuple('Segment', ['text', 'attributes', 'syntax_attrs'])

    def __init__(self, list_of_segments=None, default_attr=curses.A_NORMAL):
        """Can provide a list of strings, each string will become one segment
        with it's own curses attributes, segments passed this way will get the
        default curses attributes"""
        if not list_of_segments:
            list_of_segments = []
        self.line_segments = []  # a list of line_segment tuples

        # Set the default attribute for this line
        self.default_attr = default_attr

        assert not isinstance(list_of_segments, string_types), \
            'Argument to Line must be a list of strings'

        for segment in list_of_segments:
            if isinstance(segment, Line.Segment):
                # This is already a segment type, so just add it to the list
                self.line_segments.append(segment)
            else:
                # Otherwise init a new segment
                self.add_segment(segment)

    def add_segment(self, segment_text, segment_attributes=None,
                    syntax_attrs=None):
        """Add a new segment to the line, with specific attributes.
        This allows you to have a single line be coloured differently or have
        portions standout or bold, etc"""
        if not segment_attributes:
            segment_attributes = self.default_attr
        else:
            assert type(segment_attributes) is int

        self.line_segments.append(Line.Segment(segment_text,
                                               segment_attributes,
                                               syntax_attrs))

    def full_text(self):
        """Returns the entire text of the line, combining all text from each
        segments. This returns the line with no default_attr"""
        ret = ''

        for segment in self.line_segments:
            ret = ret + segment.text

        return ret

    def get_sub_line(self, start, end):
        """Return a new Line that only contains text up to <width>"""
        num_chars_so_far = 0
        ret_segment_list = []

        if start < 0 or start > end:
            raise Exception('Invalid start arg given to Line.get_sub_line')

        for segment in self.line_segments:
            if start > num_chars_so_far:
                # Check if we should begin collecting segments
                if len(segment.text) + num_chars_so_far > start:
                    # Check how much of this segment that just pushes into the
                    # collection range should be included
                    chars_to_take = ((len(segment.text) + num_chars_so_far) -
                                     start)
                    ret_segment_list.append(
                        Line.Segment(segment.text[-chars_to_take:],
                                     segment.attributes,
                                     segment.syntax_attrs))
            else:
                if len(segment.text) + num_chars_so_far < end:
                    ret_segment_list.append(segment)
                else:
                    # We can't fit the entirety of the next segment, but check
                    # if a subset will fit
                    num_chars_remaining = end - num_chars_so_far
                    if num_chars_remaining:
                        ret_segment_list.append(Line.Segment(
                            segment.text[:num_chars_remaining],
                            segment.attributes,
                            segment.syntax_attrs))
                    break
            num_chars_so_far += len(segment.text)

        return Line(ret_segment_list, default_attr=self.default_attr)

    def highlight_str(self, str_to_highlight, highlight_attr):
        """Takes an input string to highlight and searches for instances of it
        (even across segment boundaries), creating a new segment for each hit
        and changing it's curses attribute to highlight.
        Returns a new Line object"""
        # print('string to highlight: %s' % str_to_highlight)
        search_str_re = re.escape(str_to_highlight)
        # print('string to highlight re: %s' % search_str_re)
        segments = self.line_segments
        for start_pos in [match.start() for match in
                          re.finditer('(%s)' % search_str_re,
                                      self.full_text())]:
            # print('working on start_pos: %d' % start_pos)
            segments = self._split_new_segment(start_pos,
                                               start_pos+len(str_to_highlight),
                                               highlight_attr, segments)
        return Line(segments)

    def _split_new_segment(self, start, end, attributes, segments):
        """Cut a new segment out at <start>, <end>, giving it the curses
        attributes <attributes>.
        Returns a new segment list"""
        new_segments = []
        new_seg_len = end-start
        done_split = False
        if start < 0 or start > end:
            raise Exception('Invalid start arg given to Line.get_sub_line')

        num_chars_so_far = 0
        remaining_chars = -1
        # print('start %d' % start)
        # print('end %d' % end)
        # print('full_text:  %s' % ':'.join([seg.text for seg in segments]))
        segments = iter(segments)
        for segment in segments:
            seg_len = len(segment.text)
            # print('working on seg %s, with len: %d' % (segment, seg_len))
            # print('num_chars_so_far: %d' % num_chars_so_far)
            if not done_split and start >= num_chars_so_far:
                # print('checking if we\'ve reached start yet')
                if seg_len + num_chars_so_far > start:
                    # print('we\'ve reached the start!')
                    # We've found the split point
                    (prev_s, new_s,
                     next_s) = substring_split(start-num_chars_so_far,
                                               end-num_chars_so_far,
                                               segment.text)
                    # print('prev_s: %s' % prev_s)
                    if prev_s:
                        prev_seg = Line.Segment(prev_s,
                                                segment.attributes,
                                                segment.syntax_attrs)
                        # print('prev_seg: %s' % prev_seg.text)
                        new_segments.append(prev_seg)

                    # print('new_s: %s' % new_s)
                    # grab the full substring here. We'll skip all segments
                    # that fall into this range down below
                    if not attributes:
                        attributes = segment.attributes
                    new_segments.append(
                        Line.Segment(self.full_text()[start:end], attributes,
                                     None))

                    # print('next_s: %s' % next_s)
                    if next_s:
                        next_seg = Line.Segment(next_s,
                                                segment.attributes,
                                                segment.syntax_attrs)
                        # print('next_seg: %s' % next_seg.text)
                        new_segments.append(next_seg)

                    remaining_chars = new_seg_len - len(new_s)
                    done_split = True
                    num_chars_so_far += len(segment.text)
                    continue

            if remaining_chars > 0:
                # print('remaining_chars: %d' % remaining_chars)
                if remaining_chars < seg_len:
                    # print('We need a portion of this segment')
                    # We need a portion of this line
                    # Modify the segment following this one to remove any
                    # pieces that belong to the new segment
                    next_seg = Line.Segment(
                        segment.text[remaining_chars:],
                        segment.attributes,
                        segment.syntax_attrs)
                    new_segments.append(next_seg)
                else:
                    # print('we need all of the chars from this seg, continue'
                    #       ' skipping this line')
                    pass
                remaining_chars -= seg_len
                num_chars_so_far += len(segment.text)
                continue

            new_segments.append(segment)
            num_chars_so_far += len(segment.text)

        return new_segments

    def __len__(self):
        return len(self.line_segments)

    def __getitem__(self, index):
        return self.line_segments[index]

    def __setitem__(self, index, value):
        raise NotImplementedError('__setitem__ not implemented, please use the'
                                  'add_segment method')


class BaseContent:
    """A base class for the git objects (blame and show)
    Comes with len and get/set overrides and the methods to compress and
    uncompress the lines attribute"""
    __metaclass__ = ABCMeta

    default_attr = curses.A_NORMAL
    default_str = '~'

    @abstractmethod
    def __init__(self):
        # To be called after subclasses __init__ work is done

        # self.lines comes from subclasses, init it again here to make pylint
        # happy
        self.lines = self.lines  # Satisfy pylint

        # lines will grow if any '~' padding is added
        self.numlines = len(self.lines)
        # Collect after any deleted objects
        gc.collect()

    @abstractmethod
    def buildlinesdict(self, lines):
        """build a default dict with schema:
        index --> Line(line or <defaultstr>, curses str attributes)
        The default string makes scrolling past the edge of the file much more
        graceful.
        I.e. having a default value rather than handling IndexError and then
        returning the default string.
        This function will add a default or the provided attribute to each
        line.  The lines can be further decorated at later times by logically
        OR-ing in other attributes to the attribute set here. Classes that need
        to do more advanced processing of the lines, should override this
        method"""
        logging.info('running base buildlinesdict')
        ret_lines_dict = self.gen_default_lines_dict()
        for idx, line in enumerate(lines):
            ret_lines_dict[idx] = Line([line], BaseContent.default_attr)

        return ret_lines_dict

    def gen_default_lines_dict(self):
        """Return a default dict with the proper schema to be used for a lines
        dictionary"""
        return defaultdict(lambda: (Line([BaseContent.default_str],
                                         BaseContent.default_attr)))

    def __len__(self):
        return self.numlines

    def __getitem__(self, index):
        return self.lines[index]

    def __setitem__(self, index, value):
        self.lines[index] = value

    def compress(self):
        """Compress the lines attribute which stores the content of the lines
        attribute. This makes storing each stack frame cheaper"""
        # XXX: compress/decompress currently broken by new Line Segments
        # feature. It's more difficult to compress the lines (with a good
        # compression ratio) as well as keeping the curses attributes for each
        # segment. Will address this feature at a later date (either fixing or
        # removing this feature)
        # pylint: disable=unreachable
        return

        blame_text = '\n'.join([line.full_text()
                                for line in self.lines.values()])
        compressed_lines = zlib.compress(blame_text.encode('utf-8'))
        del self.lines
        gc.collect()
        self.lines = compressed_lines

    def decompress(self):
        """Decompress the lines attribute which stores the content of the git
        blame."""
        # XXX: compress/decompress currently broken by new Line Segments
        # feature. It's more difficult to compress the lines (with a good
        # compression ratio) as well as keeping the curses attributes for each
        # segment. Will address this feature at a later date (either fixing or
        # removing this feature)
        # pylint: disable=unreachable
        return

        temp_lines = zlib.decompress(self.lines)
        # We don't need any special processing at this point, since it was
        # already done and we're just re-hydrating it from concentrate
        self.lines = BaseContent.buildlinesdict(self, temp_lines.splitlines())
        del temp_lines
        gc.collect()


# In this case I really do want an object pylint, but thanks...
# pylint: disable=R0903
class BidirectionalCycle(object):
    """A cycle iterator that can iterate in both directions (e.g. has next
    and prev).
    This is a simple object that supports the iterator protocol but it doesn't
    behave like one might expect a standard iterator to (e.g. a generator that
    lazily produces the next value) this object will keep the WHOLE LIST in
    memory, so use WITH CAUTION
    >>> bi_iter = BidirectionalCycle([0, 1, 2])
    >>> bi_iter.next()
    0
    >>> bi_iter.next()
    1
    >>> bi_iter.next()
    2
    >>> bi_iter.next()
    0
    >>> bi_iter.prev()
    2
    >>> bi_iter.prev()
    1
    >>> bi_iter.prev()
    0
    >>> bi_iter.prev()
    2
    >>> bi_iter = BidirectionalCycle([0, 1, 2], starting_index=1)
    >>> bi_iter.next()
    1
    >>> bi_iter = BidirectionalCycle([0, 1, 2], starting_index=1)
    >>> bi_iter.prev()
    1
    >>> bi_iter = BidirectionalCycle([0, 1, 2], starting_index=1, no_wrap=True)
    >>> bi_iter.next()
    1
    >>> bi_iter.next()
    2
    >>> bi_iter.next()
    Traceback (most recent call last):
    ...
    StopIteration
    """
    def __init__(self, list_seq, starting_index=0, no_wrap=False):
        self.current_index = self.init_index = starting_index
        # CURRENTLY ONLY SUPPORT LISTS
        assert isinstance(list_seq, list), 'Currently only supports lists'
        self.seq = list_seq
        self.no_wrap = no_wrap
        self.start_of_day = True

    def next(self):
        """Maintain support for python2 iterator"""
        return self.__next__()

    def __next__(self):
        """return the next item in the iteration"""
        self._check_len()
        if self.start_of_day:
            return self._start_of_day()

        self._move_index_next()
        next_item = self.seq[self.current_index]

        return next_item

    def prev(self):
        """return the previous item in the iteration"""
        self._check_len()
        if self.start_of_day:
            if self.no_wrap:
                raise StopIteration()
            return self._start_of_day()

        self._move_index_prev()
        prev_item = self.seq[self.current_index]

        return prev_item

    def curr(self):
        """Returns the current item in the iteration"""
        self._check_len()
        if self.start_of_day:
            return self._start_of_day()

        return self.seq[self.current_index]

    def _move_index_next(self):
        """Move the index in the next direction"""
        # check if we need to wrap around to the beginning
        if self.current_index == len(self.seq) - 1:
            if self.no_wrap:
                raise StopIteration()
            self.current_index = 0
        else:
            self.current_index = self.current_index + 1

    def _move_index_prev(self):
        """Move the index in the prev direction"""
        # check if we need to wrap around to the end
        if self.current_index == 0:
            if self.no_wrap:
                raise StopIteration()
            self.current_index = len(self.seq) - 1
        else:
            self.current_index = self.current_index - 1

    def _check_len(self):
        """As itertools.cycle does, raise StopIteration if the sequence
        is empty"""
        if len(self.seq) == 0:
            raise StopIteration

    def _start_of_day(self):
        """print out the init_index of the sequence and set start_of_day to
        false. This is needed to get the behaviour that after init-ing the
        iterator if you call either previous or next, you get the starting
        index."""
        self.start_of_day = False
        return self.seq[self.init_index]

    def __str__(self):
        return str(self.seq)

    def __iter__(self):
        return self

    def __len__(self):
        return len(self.seq)

    def __contains__(self, item):
        return item in self.seq
