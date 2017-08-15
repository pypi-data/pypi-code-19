"""
This module provides basic arithmetic for even-tempered western musical notes.


This module provides the following classes:

    Note: represents a musical note
    Interval: represents the interval between two notes


It also provides the following utility functions:

    get_midi_number(note_string) -> midi number
    in_chord(note, root, chord) -> boolean


The following intervals are predefined:

    P1 = unison = Interval(0)
    m2 = semitone = Interval(1)
    M2 = Interval(2)
    m3 = Interval(3)
    M3 = Interval(4)
    P4 = Interval(5)
    aug4 = dim5 = Interval(6)
    P5 = Interval(7)
    m6 = Interval(8)
    M6 = Interval(9)
    m7 = Interval(10)
    M7 = Interval(11)
    P8 = octave = Interval(12)


The following chord types are predefined:

    MAJOR = (unison, M3, P5)
    MINOR = (unison, m3, P5)
    SEVENTH = (unison, M3, P5, m7)
"""

from __future__ import division, print_function, unicode_literals


# Used to map note strings to their MIDI values
NOTE_NAMES = {
    'cb': 11,
    'c-': 11,
    'c': 12,
    'c#': 13,
    'c+': 13,
    'db': 13,
    'd-': 13,
    'd': 14,
    'd#': 15,
    'd+': 15,
    'eb': 15,
    'e-': 15,
    'e': 16,
    'fb': 16,
    'f-': 16,
    'e#': 17,
    'e+': 17,
    'f': 17,
    'f#': 18,
    'f+': 18,
    'gb': 18,
    'g-': 18,
    'g': 19,
    'g#': 20,
    'g+': 20,
    'ab': 20,
    'a-': 20,
    'a': 21,
    'a#': 22,
    'a+': 22,
    'bb': 22,
    'b-': 22,
    'b': 23,
    'b#': 24,
    'b+': 24,
}


class Interval(object):
    """
    Represents a specific musical interval. Supports basic arithmetic.

    >>> P4
    Interval(5)
    >>> P4 + P5
    Interval(12)
    >>> P4 + P5 == octave
    True
    >>> P5 - P4 == Interval(2)
    True
    >>> P4 - P5
    Interval(-2)
    >>> P4 * 2
    Interval(10)
    >>> P4
    Interval(5)
    >>> aug4
    Interval(6)
    >>> aug4 / 2
    Interval(3)
    >>> P4 / 2
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: unsupported operand type(s) for /: 'Interval' and 'int'
    >>> P4 // 2
    Interval(2)
    >>> P5 % m3
    Interval(1)
    >>> P5 / M3
    1.75
    """

    def __init__(self, value):
        self.semitones = value

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.semitones)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.semitones == other.semitones

    def __hash__(self):
        return hash(self.semitones)

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.semitones + other.semitones)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, self.__class__):
            return self + -other
        return NotImplemented

    def __neg__(self):
        return self.__class__(-self.semitones)

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__(self.semitones * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __div__(self, other):
        if isinstance(other, self.__class__):
            return self.semitones / other.semitones
        if self.semitones % other == 0:
            return self.__class__(self.semitones // other)
        return NotImplemented

    def __truediv__(self, other):
        return self.__div__(other)

    def __floordiv__(self, other):
        if isinstance(other, self.__class__):
            return self.semitones // other.semitones
        return self.__class__(self.semitones // other)

    def __mod__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.semitones % other.semitones)
        return NotImplemented

    def __divmod__(self, other):
        if isinstance(other, self.__class__):
            return (self.__floordiv__(other), self.__mod__(other))
        return NotImplemented


def get_midi_number(note_string):
    """
    Accepts a note string (e.g. 'c5', 'e-3') and returns the MIDI note number
    for that note. A valid note string consists of:

    1. a note letter (case insensitive)
    2. optional accidental indicator (sharp: # or +; flat: b or -)
    3. optional octave number (defaults to 4 if omitted)
    """

    i = 1
    while note_string[-i].isdigit():
        if i >= len(note_string):
            raise TypeError('invalid note string')
        i += 1
    if i == 1:
        letter = note_string
        octave_number = 4
    else:
        letter = note_string[:1 - i]
        octave_number = int(note_string[1 - i:])

    midi_number = NOTE_NAMES[letter.lower()]
    midi_number += 12 * octave_number
    return midi_number


# Pre-defined intervals
P1 = unison = Interval(0)
m2 = semitone = Interval(1)
M2 = Interval(2)
m3 = Interval(3)
M3 = Interval(4)
P4 = Interval(5)
aug4 = dim5 = Interval(6)
P5 = Interval(7)
m6 = Interval(8)
M6 = Interval(9)
m7 = Interval(10)
M7 = Interval(11)
P8 = octave = Interval(12)


class Note(object):
    """
    Represents a musical note. Supports basic arithmetic.

    >>> Note('c')
    Note(60)
    >>> Note('a-2')
    Note(44)
    >>> Note('c') - Note('a-2')
    Interval(16)
    >>> Note('c') + M3
    Note(64)
    >>> (Note('c3') + P5).get_note_string()
    'G3'
    """

    # Class used for difference between notes
    INTERVAL_CLASS = Interval

    # Used for converting note value to string
    NOTE_STRINGS = {
        P1: 'C',
        m2: 'C#',
        M2: 'D',
        m3: 'D#',
        M3: 'E',
        P4: 'F',
        dim5: 'F#',
        P5: 'G',
        m6: 'G#',
        M6: 'A',
        m7: 'A#',
        M7: 'B',
    }

    def __init__(self, value):
        if isinstance(value, (type(b''), type(u''))):
            midi_number = get_midi_number(value)
        else:
            midi_number = value

        self.midi_number = midi_number

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.midi_number)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.midi_number == other.midi_number

    def __hash__(self):
        return hash(self.midi_number)

    def __sub__(self, other):
        if isinstance(other, self.__class__):
            return self.INTERVAL_CLASS(self.midi_number - other.midi_number)
        if isinstance(other, self.INTERVAL_CLASS):
            return self + -other
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, self.INTERVAL_CLASS):
            return self.__class__(self.midi_number + other.semitones)
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def get_note_string(self):
        """
        Returns a valid note string for this note.

        >>> Note(85).get_note_string()
        'C#6'
        """
        octave_number, interval = divmod(self - Note('c0'), octave)
        return self.NOTE_STRINGS[interval] + str(octave_number)



# Pre-defined chord types
MAJOR = (unison, M3, P5)
MINOR = (unison, m3, P5)
SEVENTH = (unison, M3, P5, m7)


def in_chord(note, root, chord):
    """
    Returns True if the given note is in the given chord on the given root.
    Ignores the octave of the note, or inversion of the chord, simply says
    whether the given note could be a part of the given chord on the given
    root.

    >>> in_chord(Note('c5'), Note('a'), MINOR)
    True
    >>> in_chord(Note('c5'), Note('a'), MAJOR)
    False
    """
    return (note - root) % octave in chord
