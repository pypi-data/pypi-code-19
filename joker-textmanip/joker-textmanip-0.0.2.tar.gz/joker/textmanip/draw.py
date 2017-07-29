#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function


def make_title_box(title, comment='#', width=50):
    """
    # +--------------------------------------------------+
    # |                                                  |
    # |                  Title is here                   |
    # |                                                  |
    # +--------------------------------------------------+
    """
    lines = list()
    lines.append('+{}+'.format('-' * width))
    lines.append('|{}|'.format(' ' * width))
    lines.append('|{}|'.format(title.center(width)))
    lines.append('|{}|'.format(' ' * width))
    lines.append('+{}+'.format('-' * width))
    return ''.join(('{} {}\n'.format(comment, l) for l in lines))

