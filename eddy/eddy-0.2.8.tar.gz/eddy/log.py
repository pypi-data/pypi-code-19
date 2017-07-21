import logging
import sys
import time

def supports_color():
    """
    Returns True if the running system's terminal supports color,
    and False otherwise.
    from django.core.management.color
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and \
        (plat != 'win32' or 'ANSICON' in os.environ)

    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    if not supported_platform or not is_a_tty:
        return False
    return True

class BaseFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None):
        FORMAT = '%(asctime)s %(customlevelname)s\t%(message)s'
        super(BaseFormatter, self).__init__(fmt=FORMAT, datefmt=datefmt)

    def format(self, record):
        customlevel = self._get_levelname(record.levelname)
        record.__dict__['customlevelname'] = customlevel
        # format multiline messages 'nicely' to make it clear they are together
        record.msg = record.msg.replace('\n', '\n  | ')
        return super(BaseFormatter, self).format(record)

    def formatTime(self, record, datefmt=None):
        if datefmt:
            s = time.strftime(datefmt)
        else:
            t = time.strftime("%H:%M:%S")
            s = "%s" % (t)
        return s

    def formatException(self, ei):
        ''' prefix traceback info for better representation '''
        # .formatException returns a bytestring in py2 and unicode in py3
        # since .format will handle unicode conversion,
        # str() calls are used to normalize formatting string
        s = super(BaseFormatter, self).formatException(ei)
        # fancy format traceback
        s = str('\n').join(str('  | ') + line for line in s.splitlines())
        # separate the traceback from the preceding lines
        s = str('  |___\n{}').format(s)
        return s

    def _get_levelname(self, name):
        ''' NOOP: overridden by subclasses '''
        return name

class ANSIFormatter(BaseFormatter):
    ANSI_CODES = {
        'green': '\033[1;32m',
        'red': '\033[1;31m',
        'yellow': '\033[1;33m',
        'cyan': '\033[1;36m',
        'white': '\033[1;37m',
        'bgred': '\033[1;41m',
        'bggrey': '\033[1;100m',
        'reset': '\033[0;m'}

    LEVEL_COLORS = {
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bgred',
        'DEBUG': 'cyan'}

    NAMES = {
        'INFO': 'INFO',
        'WARNING': 'WARN',
        'ERROR': 'ERROR',
        'CRITICAL': 'CRIT',
        'DEBUG': 'DEBUG'}


    def _get_levelname(self, name):
        color = self.ANSI_CODES[self.LEVEL_COLORS.get(name, 'white')]
        fmt = '{0}{1}{2}:'
        return fmt.format(color, self.NAMES[name], self.ANSI_CODES['reset'])

class TextFormatter(BaseFormatter):
    """
    Convert a `logging.LogRecord' object into text.
    """

    def _get_levelname(self, name):
        if name == 'INFO':
            return '->'
        else:
            return name + ':'

def formatter():
    if supports_color():
        return ANSIFormatter()
    else:
        return TextFormatter()

def init_logging(name, level, out=sys.stderr):
    handler = logging.StreamHandler(out)
    logger = logging.getLogger(name)

    handler.setFormatter(formatter())
    logger.addHandler(handler)

    if level:
        logger.setLevel(level)

    return logger
