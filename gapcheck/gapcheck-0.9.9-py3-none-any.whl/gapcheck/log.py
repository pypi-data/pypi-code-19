# -*- coding: utf-8 -*-

import sys
import os
import datetime


def gen_loginfo(options, olddir, checked, gaps, ignored, filesgaps):
    """ Genera un diccionario con el log, que luego podré usar para
        sacar un log precioso o bien un fichero o ambos """

    loginfo = dict()

    loginfo['directory'] = os.path.abspath(olddir)
    loginfo['date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    loginfo['extension'] = str(options.extension)
    loginfo['sox_last_seconds'] = str(options.seconds)
    loginfo['sox_max_amplitude'] = str(options.max_amplitude)
    loginfo['files_checked'] = str(checked)
    loginfo['files_ignored'] = str(ignored)
    loginfo['files_with_gap'] = str(gaps)

    loginfo['list_files_with_gap'] = list()
    for fg in filesgaps:
        if fg['gap']:
            loginfo['list_files_with_gap'].append(fg['basename'])

    return loginfo


def gen_loginfo_join(filenames, filedest):
    """ Genera un diccionario de log para la parte del join """
    loginfo = dict()
    loginfo['file_joined'] = os.path.basename(filedest)
    loginfo['list_files_joined'] = list()
    for fn in filenames:
        loginfo['list_files_joined'].append(os.path.basename(fn))

    return loginfo


def loginfo_join_to_file(loginfo, f):

    print('file_joined: ' + loginfo['file_joined'], file=f)
    for fn in loginfo['list_files_joined']:
        print(' - ' + fn, file=f)


def loginfo_to_file(loginfo, f):
    """ Escribe en el directorio que se ha analizado un loginfo """

    print('directory: ' + loginfo['directory'], file=f)
    print('date: ' + loginfo['date'], file=f)
    print('extension: ' + loginfo['extension'], file=f)
    print('sox_last_seconds: ' + loginfo['sox_last_seconds'], file=f)
    print('sox_max_amplitude: ' + loginfo['sox_max_amplitude'], file=f)
    print('files_checked: ' + loginfo['files_checked'], file=f)
    print('files_ignored: ' + loginfo['files_ignored'], file=f)
    print('files_with_gaps: ' + loginfo['files_with_gap'], file=f)
    for fn in loginfo['list_files_with_gap']:
        print(' - ' + fn, file=f)


def write_log(options, olddir, checked, gaps, ignored, filesgaps):
    """ Unifica la escritura de log, tanto por pantalla como a fichero """

    loginfo = gen_loginfo(options, olddir, checked, gaps, ignored, filesgaps)

    # TODO esto ya no es necesario ya que los ficheros con los backups ya no
    # tienen ficheros *FLAC o similar

    # Así ignoramos los directorios donde se guardan las copias de seguidad
    # de los ficheros
    if checked != ignored and checked > 0:
        logfile = open(os.path.join(olddir, 'gapcheck.log'), 'a')
        loginfo_to_file(loginfo, logfile)

    loginfo_to_file(loginfo, sys.stdout)


def write_join_log(options, filenames, filedest):
    """ """
    loginfo = gen_loginfo_join(filenames, filedest)

    if len(filenames):
        pathlog = os.path.abspath(os.path.dirname(filedest))
        logfile = open(os.path.join(pathlog, 'gapcheck.log'), 'a')
        loginfo_join_to_file(loginfo, logfile)

    loginfo_join_to_file(loginfo, sys.stdout)
