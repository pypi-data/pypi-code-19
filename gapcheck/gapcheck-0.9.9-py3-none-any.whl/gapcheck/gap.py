# -*- coding: utf-8 -*-

import os
import sox


def check_if_gap(filename, seconds, max_amplitude):
    """ Revisa si existe GAP y lo hacemos mirando los últimos segundos del
        tema y ver si tiene una amplitud alta, en ese caso tiene GAP """

    extension = os.path.splitext(filename)[1][1:]
    tempfilename = 'tmp.' + extension

    total_seconds = sox.file_info.duration(filename)

    start = total_seconds - seconds
    end = total_seconds

    tfm = sox.Transformer()
    tfm.trim(start, end)
    tfm.build(filename, tempfilename)

    stat = sox.file_info.stat(tempfilename)

    os.remove(tempfilename)

    return bool(stat['Maximum amplitude'] > max_amplitude)
