# -*- coding: utf-8 -*-

import glob
import os
from operator import itemgetter
from gapcheck import buildparser
from gapcheck import gap
from gapcheck import join
from gapcheck import log


def all_files(path, ext):
    """ Return list of all files in path with extension ext """
    pathname = '{}/**/*.{}'.format(path, ext)

    return glob.glob(pathname, recursive=True)


def check_if_ignore(filename):
    """ Revisamos por si ya hubieramos chequeado el fichero:
        1. Existe el fichero gapcheck.log en el mismo directorio """

    file_check = 'gapcheck.log'

    if os.path.isfile(os.path.join(os.path.dirname(filename), file_check)):
        return True

    return False


def gapcheck(options):

    checked = 0
    gaps = 0
    ignored = 0
    olddir = ''
    first = True
    filesgaps = list()

    # Recuperamos recursivamente TODOS los ficheros con options.extension
    files = all_files(options.path, options.extension)

    # files.sort()

    for filename in files:

        if first:
            first = False
            olddir = os.path.abspath(os.path.dirname(filename))
        else:
            # aquí montar el log de directorios
            curdir = os.path.abspath(os.path.dirname(filename))
            if curdir != olddir:

                # TODO no es necesario tanta variable
                files = sorted(filesgaps, key=itemgetter('filename'))
                log.write_log(options, olddir, checked, gaps, ignored, files)
                join.join_files(options, files)

                olddir = curdir
                checked = 0
                gaps = 0
                ignored = 0
                filesgaps = list()

        checked += 1

        if not options.force_analyze and check_if_ignore(filename):
            ignored += 1
            continue

        filechecked = dict()
        filechecked['basename'] = os.path.basename(filename)
        filechecked['filename'] = filename
        filechecked['gap'] = False

        if gap.check_if_gap(filename, options.seconds, options.max_amplitude):
            filechecked['gap'] = True
            gaps += 1

        filesgaps.append(filechecked)

    # el caso es que siempre el último no se mostrará, lo sacamos ahora
    files = sorted(filesgaps, key=itemgetter('filename'))
    log.write_log(options, olddir, checked, gaps, ignored, files)
    join.join_files(options, files)


def main():

    # Yeah
    parser = buildparser.build_parser()

    options = parser.parse_args()

    # Yeah x 2
    # te gusta pasarle el parser? mmm no lo tengo claro
    gapcheck(options)


if __name__ == '__main__':
    main()
