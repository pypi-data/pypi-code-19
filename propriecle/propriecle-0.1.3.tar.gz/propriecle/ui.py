"""All the UI Widgets we need, and probably more"""

import curses
import time


def init_screen():
    """Initialize our base curses constructs. Sets up the screen object, sets
    our default color pairs, and sets basic terminal options."""
    screen = curses.initscr()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # default
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # OK
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)  # NOT OK
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_RED)  # alart
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_RED)  # alart effect
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)  # selection
    curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # selection

    # do not display curses, or echo anything
    curses.curs_set(0)
    curses.cbreak()
    curses.noecho()
    # capture keys!
    screen.keypad(1)
    return screen


def popup(screen, msg):
    """Generate a popup message that requires a acknoledgement"""
    middle_y, middle_x = middle_yx(screen)
    my_x = len(msg) + 6
    my_y = 3
    win = curses.newwin(my_y, my_x, middle_y - my_y, middle_x - my_x)
    screen.refresh()
    win.border()
    win.bkgd(ord(' '), curses.color_pair(1))
    string_at(win, 1, 0, msg, curses.color_pair(7), 'center')
    start = time.time()
    while True:
        win.refresh()
        screen.timeout(500)
        if screen.getch() != -1 or time.time() - start > 2:
            win.erase()
            win.refresh()
            del win
            return


def yesno(screen, msg):
    """Generate a popup message that a user can accept or cancel"""
    middle_y, middle_x = middle_yx(screen)
    my_x = len(msg) + 6
    my_y = 4
    win = curses.newwin(my_y, my_x, middle_y - my_y, middle_x - my_x)
    screen.refresh()

    win.border()
    win.bkgd(ord(' '), curses.color_pair(1))
    string_at(win, 1, 0, msg, curses.color_pair(2), 'center')
    done = False
    blink = False
    msg_yes = '[Y]es'
    msg_no = '[N]o'
    anim_x = (my_x/2) + (len(msg)/2)
    while not done:
        if not blink:
            string_at(win, 1, anim_x, '?', curses.color_pair(2))
            string_at(win, 2, 2, msg_yes,
                      curses.color_pair(2) | curses.A_BOLD)
            string_at(win, 2, -2, msg_no, curses.color_pair(2), 'right')
            blink = True
        else:
            string_at(win, 1, anim_x, ' ', curses.color_pair(2))
            string_at(win, 2, 2, msg_yes, curses.color_pair(2))
            string_at(win, 2, -2, msg_no,
                      curses.color_pair(2) | curses.A_BOLD, 'right')
            blink = False

        win.refresh()
        screen.timeout(500)
        ch = screen.getch()
        if ch == ord('y') or ch == ord('Y'):
            pulse(win, 2, 2, msg_yes, 'left')
            del win
            return True
        elif ch == ord('n') or ch == ord('N') or ch == 27:
            pulse(win, 2, -2, msg_no, 'right')
            del win
            return False


def pulse(win, y, x, msg, align):
    """Generates some prettily pulsing text"""
    for f in range(1, 6):
        if f % 2 == 0:
            string_at(win, y, x, msg, curses.color_pair(2), align)
        else:
            string_at(win, y, x, msg, curses.color_pair(3), align)

        win.refresh()
        curses.napms(200)


def middle_yx(screen):
    """Determins the middle of the screen"""
    xy = screen.getmaxyx()
    screen_y = xy[0]
    screen_x = xy[1]
    return screen_y/2, screen_x/2


def string_at(win, y, x_base, msg, attr, align='left'):
    """Places a string at a particular place on the screen."""
    x = win.getmaxyx()[1]
    str_x = 1
    if align == 'center':
        str_x = (x/2)-(len(msg)/2)
    elif align == 'right':
        str_x = x - len(msg) - 1

    str_x = str_x + x_base

    win.addstr(y, str_x, msg, attr)


def ask_for(screen, msg):
    """Text input funciton. Pretty terrible, tbh."""
    middle_y, middle_x = middle_yx(screen)
    window_width = len(msg) + 10
    win_x = middle_x - (window_width/2)
    win_y = middle_y - 10
    win = curses.newwin(4, window_width, win_y, win_x)
    screen.refresh()
    win.border()
    win.bkgd(ord(' '), curses.color_pair(1))
    win.addstr(1, (window_width / 2) - (len(msg) / 2),
               msg, curses.color_pair(2))
    resp = ''
    done = False
    step = 0
    steps = ['/', '|', '\\', '-']
    while not done:
        win.refresh()
        screen.timeout(500)
        ch = screen.getch()
        if ch == 27:
            win.erase()
            win.refresh()
            del win
            return None
        elif ch == 10:
            win.erase()
            win.refresh()
            del win
            done = True
        else:
            if ch != -1:
                resp = "%s%s" % (resp, chr(ch))
            else:
                win.addch(1,
                          (window_width/2) + (len(msg)/2) + 2,
                          ord(steps[step]),
                          curses.color_pair(2) | curses.A_BOLD)
                if step == len(steps) - 1:
                    step = 0
                else:
                    step = step + 1

    return resp
