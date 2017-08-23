import colorsys

C4B_BLACK = '0'
C4B_RED = '1'
C4B_GREEN = '2'
C4B_YELLOW = '3'
C4B_BLUE = '4'
C4B_MAGENTA = '5'
C4B_CYAN = '6'
C4B_WHITE = '7'
C4B_EXTENDED = '8'
C4B_DEFAULT = '9'

COLOR_NAMES = {
    'black': C4B_BLACK,
    'red': C4B_RED,
    'green': C4B_GREEN,
    'yellow': C4B_YELLOW,
    'blue': C4B_BLUE,
    'magenta': C4B_MAGENTA,
    'cyan': C4B_CYAN,
    'white': C4B_WHITE,
}

FLAG_RESET = '0'
FLAG_BOLD = '1'
FLAG_BOLD_OFF = '21'  # Not widely supported
FLAG_FAINT = '2'
FLAG_NORMAL = '22'  # Neither bold nor faint
FLAG_ITALIC = '3'
FLAG_ITALIC_OFF = '23'
FLAG_UNDERLINE = '4'
FLAG_UNDERLINE_OFF = '24'
FLAG_BLINK = '5'
FLAG_BLINK_OFF = '25'
FLAG_BLINK_RAPID = '6'
FLAG_NEGATIVE = '7'
FLAG_POSITIVE = '27'
FLAG_CONCEAL = '8'
FLAG_REVEAL = '28'
FLAG_CROSSED = '9'
FLAG_CROSSED_OFF = '29'

FLAG_FOREGROUND = '3'
FLAG_BACKGROUND = '4'


def make_ansi_escape(
        fg=None, bg=None, reset=False, bold=False, faint=False, italic=False,
        underline=False, blink=False, negative=False, crossed=False):

    flags = filter(None, [
        FLAG_RESET if reset else None,
        FLAG_BOLD if bold else None,
        FLAG_FAINT if faint else None,
        FLAG_ITALIC if italic else None,
        FLAG_UNDERLINE if underline else None,
        FLAG_BLINK if blink else None,
        FLAG_NEGATIVE if negative else None,
        FLAG_CROSSED if crossed else None,
        '{}{}'.format(FLAG_FOREGROUND, fg) if fg else None,
        '{}{}'.format(FLAG_BACKGROUND, bg) if bg else None,
    ])
    if flags:
        return ''  # No need to generate an escape code
    return '\x1b[{}m'.format(';'.join(flags))


def ansi_4bit(name):
    return COLOR_NAMES[name]


def ansi_16col(name, high=False):
    color = COLOR_NAMES[name]
    if high:
        color = str(int(color) + 8)
    return '8;5;{}'.format(color)


def ansi_rgb_color(r, g, b):
    """Generate color code for an ANSI color
    """
    return '8;5;{}'.format(rgb_8bit(r, g, b))


def ansi_hsl_color(h, s, l):
    """Generate color code for an ANSI color, from HSL values.

    Args:
        h: hue, 0-1
        s: saturation, 0-1
        l: luminance, 0-1
    """
    return '8;5;{}'.format(hsl_8bit(h, s, l))


def ansi_gray(lum):
    return '8;5;{}'.format(gray_8bit(lum))


def rgb_8bit(r, g, b):
    """
    Args:
        r: red channel, 0 to 5
        g: green channel, 0 to 5
        b: blue channel, 0 to 5
    """
    return 16 + int(round(r * 36 + g * 6 + b))


def hsl_8bit(h, s=1.0, l=.5):
    r, g, b = (int(x * 5) for x in colorsys.hls_to_rgb(h, l, s))
    return rgb_8bit(r, g, b)


def gray_8bit(lum=.5):
    """Get an 8bit color code for a gray color

    Args:
        lum: luminosity, 0 to 1
    """
    # 232: darkest, 255: lightest
    return 232 + (lum * 23)
