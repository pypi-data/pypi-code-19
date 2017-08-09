# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
from mutagen.flac import FLAC
from gapcheck import log


class JoinException(Exception):
    pass


def copy_tags(filenames, filejoin):
    """ Copia los tags de filenames a join """
    extension = os.path.splitext(filejoin)[1]

    if extension == '.flac':
        tags_orig = FLAC(filenames[0])
        tags_join = FLAC(filejoin)
    else:
        return

    for item in tags_orig.items():
        tags_join[item[0]] = item[1]

    # falta añadir lo del título... pero primero lo borramos
    for ori in filenames[1:]:
        if extension == '.flac':
            tags_orig = FLAC(ori)

        # salimos si no estn presentes tracknumber o title
        if 'tracknumber' not in tags_orig or 'title' not in tags_orig:
            # TODO guarrete guarrete...
            last_track = '1'
            last_discnumber = '1'
            continue

        last_track = tags_orig['tracknumber']

        # testeamos que tengamos discnumber
        if 'discnumber' in tags_orig:
            last_discnumber = tags_orig['discnumber']
        else:
            last_discnumber = '1'

        tags_join['title'] = tags_join['title'] + tags_orig['title']

    tags_join['gapless_join'] = str(len(filenames))
    tags_join['gapless_last_track'] = last_track
    tags_join['gapless_last_discnumber'] = last_discnumber

    tags_join.save()


def get_filenamepath_join_file(first_file):
    """ Retorna el nombre del fichero que usaremos para el join """

    suf = '__GAPLESS'

    path = os.path.dirname(first_file)
    extension = os.path.splitext(first_file)[1]
    name = os.path.splitext(os.path.basename(first_file))[0] + suf
    return os.path.join(path, name + extension)


def join_gap_files(filenames, filedest):
    """ Une las pistas en `filenames` a un fichero destino `filedest` """

    pre = '__BACKUP_'
    post = '_bck'

    filenames.sort()

    # casi que de nuevo
    path_backup = os.path.join(os.path.dirname(filenames[0]), '__backup')
    extension = os.path.splitext(filenames[0])[1]
    filedestwoe = os.path.splitext(filedest)[0]

    if extension == '.flac':
        cmd = ['shntool', 'join', '-o flac', '-a' + filedestwoe] + filenames
    else:
        raise JoinException("Impossible join not FLAC files")

    cp = subprocess.run(cmd, stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)

    if cp.returncode == 0:
        copy_tags(filenames, filedest)

        # creamos el directorio y movemos los ficheros que generaron el join
        if not os.path.exists(path_backup):
            os.makedirs(path_backup)

        for f in filenames:
            new_file_name = pre + os.path.basename(f) + post
            f_backup = os.path.join(path_backup, new_file_name)
            shutil.move(f, f_backup)
    else:
        raise JoinException("Command shntool fails")


def join_files(options, filesgaps):
    """ A partir de un listado de ficheros, recupero cuales tienen y cuales no
        tienen GAP y los junto """
    if not options.join:
        return

    files_to_join = list()

    for fg in filesgaps:
        if fg['gap']:
            files_to_join.append(fg['filename'])
        else:
            if len(files_to_join) > 0:
                files_to_join.append(fg['filename'])
                namejoin = get_filenamepath_join_file(files_to_join[0])
                join_gap_files(files_to_join, namejoin)
                log.write_join_log(options, files_to_join, namejoin)

                # reset
                files_to_join = list()

    # puede darse el caso de terminar con n ficheros con gap (sí!, el último
    # puede tener gap, imagina un disco que termina de forma abrupta...
    if len(files_to_join) > 1:
        namejoin = get_filenamepath_join_file(files_to_join[0])
        join_gap_files(files_to_join, namejoin)
        log.write_join_log(options, files_to_join, namejoin)
