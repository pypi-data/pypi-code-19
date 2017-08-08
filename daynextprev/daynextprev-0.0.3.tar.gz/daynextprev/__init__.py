# -*- coding: utf-8 -*-


def is_leapyear(y):
    if y % 400 == 0:
        return True
    elif y % 100 == 0:
        return False
    elif y % 4 == 0:
        return True
    else:
        return False


def days_of_month(y, m):
    if m == 2:
        return (29 if is_leapyear(y) else 28)
    elif m in (1, 3, 5, 8, 10, 12):
        return 31
    else:
        return 30


def next_day(y, m, d):
    if d == days_of_month(y, m):
        if m == 12:
            return (y + 1, 1, 1)
        else:
            return (y, m + 1, 1)
    else:
        return (y, m, d + 1)


def prev_day(y, m, d):
    if d == 1:
        if m == 1:
            return (y - 1, 12, 31)
        else:
            bm = m - 1
            return (y, bm, days_of_month(y, bm))
    else:
        return (y, m, d - 1)
