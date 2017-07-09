# -*- coding: utf-8 -*-
"""librpi2caster - common classes, functions and definitions
for rpi2caster utility and hardware control daemons"""

from collections import deque

# interface operating modes
PUNCHING, CASTING = 'punching', 'casting'
# boolean states and row 16 addressing modes
ON, OFF, HMN, KMN, UNITSHIFT = True, False, 'HMN', 'KMN', 'unit shift'
# signals to send to the valves
OUTPUT_SIGNALS = tuple(['0075', 'S', '0005', *'ABCDEFGHIJKLMN',
                        *(str(x) for x in range(1, 15)), 'O15'])


def parse_signals(input_signals, operation_mode, row16_mode, testing_mode):
    """Prepare the incoming signals for casting, testing or punching."""
    def is_present(value):
        """Detect and dispatch known signals in source string"""
        nonlocal source
        string = str(value)
        if string in source:
            source = source.replace(string, '')
            return True
        else:
            return False

    def strip_16():
        """Get rid of the "16" signal and replace it with "15"."""
        if '16' in parsed_signals:
            parsed_signals.discard('16')
            parsed_signals.add('15')

    def convert_hmn():
        """HMN addressing mode - developed by Monotype, based on KMN.
        Uncommon."""
        # NI, NL, M -> add H -> HNI, HNL, HM
        # H -> add N -> HN
        # N -> add M -> MN
        # O -> add HMN
        # {ABCDEFGIJKL} -> add HM -> HM{ABCDEFGIJKL}

        # earlier rows than 16 won't trigger the attachment -> early return
        for i in range(1, 16):
            if str(i) in parsed_signals:
                return

        columns = 'NI', 'NL', 'H', 'M', 'N', 'O'
        extras = 'H', 'H', 'N', 'H', 'M', 'HMN'
        if '16' in parsed_signals:
            parsed_signals.discard('16')
            for column, extra in zip(columns, extras):
                if parsed_signals.issuperset(column):
                    parsed_signals.update(extra)
                    return
            parsed_signals.update('HM')

    def convert_kmn():
        """KMN addressing mode - invented by a British printshop.
        Very uncommon."""
        # NI, NL, M -> add K -> KNI, KNL, KM
        # K -> add N -> KN
        # N -> add M -> MN
        # O -> add KMN
        # {ABCDEFGHIJL} -> add KM -> KM{ABCDEFGHIJL}

        # earlier rows than 16 won't trigger the attachment -> early return
        for i in range(1, 16):
            if str(i) in parsed_signals:
                return

        columns = 'NI', 'NL', 'K', 'M', 'N', 'O'
        extras = 'K', 'K', 'N', 'K', 'M', 'HMN'
        if '16' in parsed_signals:
            parsed_signals.discard('16')
            for column, extra in zip(columns, extras):
                if parsed_signals.issuperset(column):
                    parsed_signals.update(extra)
                    return
            parsed_signals.update('KM')

    def convert_unitshift():
        """Unit-shift addressing mode - rather common,
        designed by Monotype and introduced in 1963"""
        if 'D' in parsed_signals:
            # when the attachment is on, the D signal is routed
            # to unit-shift activation piston instead of column D air pin
            # this pin is activated by EF combination instead
            parsed_signals.discard('D')
            parsed_signals.update('EF')
        if '16' in parsed_signals:
            # use unit shift if the row signal is 16
            # make it possible to shift the diecase on earlier rows
            parsed_signals.update('D')
            parsed_signals.discard('16')

    def convert_o15():
        """Change O and 15 to a combined O+15 signal"""
        for sig in ('O', '15'):
            if sig in parsed_signals:
                parsed_signals.discard(sig)
                parsed_signals.add('O15')

    def strip_o15():
        """For casting, don't use O+15"""
        parsed_signals.discard('O15')

    def add_missing_o15():
        """If length of signals is less than 2, add an O+15,
        so that when punching, the ribbon will be advanced properly."""
        convert_o15()
        if len(parsed_signals) < 2:
            # need O15 to advance the ribbon
            parsed_signals.add('O15')
        elif len(parsed_signals) > 2:
            # no need for an additional O15
            parsed_signals.discard('O15')

    def formatted_output():
        """Arrange the signals so that NI, NL will be present at the
        beginning of the signals collection"""
        arranged = deque(s for s in OUTPUT_SIGNALS if s in parsed_signals)
        # put NI, NL, NK, NJ, NKJ etc. at the front
        if 'N' in arranged:
            for other in 'JKLI':
                if other in parsed_signals:
                    arranged.remove('N')
                    arranged.remove(other)
                    arranged.appendleft(other)
                    arranged.appendleft('N')
        return list(arranged)

    try:
        source = input_signals.upper()
    except AttributeError:
        source = ''.join(str(x) for x in input_signals).upper()

    useful = ['0005', '0075', *(str(x) for x in range(16, 0, -1)),
              *'ABCDEFGHIJKLMNOS']
    parsed_signals = {s for s in useful if is_present(s)}

    # based on row 16 addressing mode,
    # decide which signal conversion should be applied
    if row16_mode == 'HMN':
        convert_hmn()
    elif row16_mode == 'KMN':
        convert_kmn()
    elif row16_mode == 'unit shift':
        convert_unitshift()
    else:
        strip_16()
    # based on the operation mode, strip, convert or add O/15 signals
    # casting: strip (as it's not used),
    # punching: add if less than 2 signals,
    # testing: convert O or 15 to O+15 which will be sent
    if testing_mode:
        convert_o15()
    elif operation_mode == 'punching':
        add_missing_o15()
    else:
        strip_o15()
    # all ready for sending
    return formatted_output()


# Exceptions
class InterfaceException(Exception):
    """Base class for interface-related exceptions"""
    message = 'General interface error.'
    offending_value = ''

    def __str__(self):
        return self.message


class MachineStopped(InterfaceException):
    """machine not turning exception"""
    code = 0
    name = 'machine stopped'


class UnsupportedMode(InterfaceException):
    """The operation mode is not supported by this interface."""
    code = 1
    name = 'unsupported operation mode'


class UnsupportedRow16Mode(InterfaceException):
    """The row 16 addressing mode is not supported by this interface."""
    code = 2
    name = 'unsupported row 16 addressing mode'


class InterfaceBusy(InterfaceException):
    """the interface was claimed by another client and cannot be used
    until it is released"""
    code = 3
    name = 'interface already in use'


class InterfaceNotStarted(InterfaceException):
    """the interface was not started and cannot accept signals"""
    code = 4
    name = 'interface not initialized'


class ConfigurationError(InterfaceException):
    """configuration error: wrong name or cannot import module"""
    code = 5
    name = 'hardware configuration error'


class CommunicationError(InterfaceException):
    """Error communicating with the interface."""
    code = 6
    message = ('Cannot communicate with the interface. '
               'Check the network connection and/or configuration.')
