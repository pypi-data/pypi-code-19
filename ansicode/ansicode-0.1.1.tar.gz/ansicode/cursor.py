def cursor_up(cells=1):
    return '\x1b[{}A'.format(cells)


def cursor_down(cells=1):
    return '\x1b[{}B'.format(cells)


def cursor_fwd(cells=1):
    return '\x1b[{}C'.format(cells)


def cursor_back(cells=1):
    return '\x1b[{}D'.format(cells)


def cursor_next_line(cells=1):
    return '\x1b[{}E'.format(cells)


def cursor_prev_line(cells=1):
    return '\x1b[{}F'.format(cells)


def cursor_horiz_abs(cells=1):
    return '\x1b[{}G'.format(cells)


def cursor_position(row=1, col=1):
    return '\x1b[{};{}H'.format(row, col)


def erase_screen(to_end=True, to_start=False, scrollback=False):
    code = (2 if to_end else 1) if to_start else 0

    if scrollback:
        code = 3

    return '\x1b[{}J'.format(code)


def erase_line(to_end=True, to_start=False):
    code = (2 if to_end else 1) if to_start else 0
    return '\x1b[{}K'.format(code)


def scroll_up(lines=1):
    return '\x1b[{}S'.format(lines)


def scroll_down(lines=1):
    return '\x1b[{}T'.format(lines)


def cursor_save():
    return '\x1b[s'


def cursor_restore():
    return '\x1b[u'
