# -*- coding: utf-8 -*-

import unittest
import sys
import os
import pathlib
import shutil
from mutagen.flac import FLAC
from gapcheck import gapcheck
from gapcheck import join
from gapcheck import log
from gapcheck import gap
from gapcheck import buildparser


class TestjoinGap(unittest.TestCase):
    """ Test join Gap """

    def setUp(self):
        """ Limpieza y generación de ficheros necesarios """
        # limpieza por si hubiera ficheros mal

        files_to_delete = ['./tests/audio/join/gapcheck.log',
                           './tests/audio/join/01-gap__GAPLESS.flac',
                           './tests/audio/join/03-gap__GAPLESS.flac',
                           './tests/audio/other/gapcheck.log',
                           './tests/audio/other/01-gap__GAPLESS.flac']

        for ftd in files_to_delete:
            if os.path.isfile(ftd):
                os.remove(ftd)

        f2mv = [['./tests/audio/join/__backup/__BACKUP_01-gap.flac_bck',
                 './tests/audio/join/01-gap.flac'],
                ['./tests/audio/join/__backup/__BACKUP_02-silence.flac_bck',
                 './tests/audio/join/02-silence.flac'],
                ['./tests/audio/join/__backup/__BACKUP_03-gap.flac_bck',
                 './tests/audio/join/03-gap.flac'],
                ['./tests/audio/join/__backup/__BACKUP_04-gap.flac_bck',
                 './tests/audio/join/04-gap.flac'],
                ['./tests/audio/join/__backup/__BACKUP_05-silence.flac_bck',
                 './tests/audio/join/05-silence.flac'],
                ['./tests/audio/other/__backup/__BACKUP_01-gap.flac_bck',
                 './tests/audio/other/01-gap.flac'],
                ['./tests/audio/other/__backup/__BACKUP_02-gap.flac_bck',
                 './tests/audio/other/02-gap.flac']]

        for ftr in f2mv:
            if os.path.isfile(ftr[0]):
                os.rename(ftr[0], ftr[1])

        dirs_to_delete = ['./tests/audio/join/__backup',
                          './tests/audio/other/__backup']

        for dtd in dirs_to_delete:
            if os.path.isdir(dtd):
                shutil.rmtree(dtd)

    def test_copy_tag(self):
        """ Test copy tag, y join """

        # 1. juntamos dos ficheros
        filedest = './tests/audio/join/01-gap__GAPLESS.flac'
        filenames = ['./tests/audio/join/01-gap.flac',
                     './tests/audio/join/02-silence.flac']
        join.join_gap_files(filenames, filedest)

        # 2. leemos los tags del fichero destino
        tags = FLAC(filedest)

        # 3. revisamos TODOS los tags
        self.assertEqual(tags['artist'], ['gapcheck'])
        self.assertEqual(tags['title'], ['Gap 01', 'Silence 02'])
        self.assertEqual(tags['album'], ['Test Join'])
        self.assertEqual(tags['date'], ['2017'])
        self.assertEqual(tags['tracknumber'], ['1'])
        self.assertEqual(tags['tracktotal'], ['6'])
        self.assertEqual(tags['gapless_join'], ['2'])
        self.assertEqual(tags['gapless_last_discnumber'], ['1'])
        self.assertEqual(tags['gapless_last_track'], ['2'])


    def test_log_join(self):
        """ Test de generacion de log """

        filedest = './tests/audio/join/01-gap__GAPLESS.flac'
        filenames = ['./tests/audio/join/01-gap.flac',
                     './tests/audio/join/02-silence.flac']

        loginfo = log.gen_loginfo_join(filenames, filedest)
        self.assertEqual(loginfo['file_joined'], '01-gap__GAPLESS.flac')
        self.assertEqual(loginfo['list_files_joined'], ['01-gap.flac',
                                                        '02-silence.flac'])

    def test_argparser_join(self):

        parser = buildparser.build_parser()

        options = parser.parse_args(['-j'])
        self.assertTrue(options.join)

        options = parser.parse_args([])
        self.assertFalse(options.join)

    def test_gapcheck_join(self):
        """ Prueba completa con join """

        # No es posible testear el directorio y la fecha...
        expected = ['directory: null',
                    'date: null',
                    'extension: flac',
                    'sox_last_seconds: 0.2',
                    'sox_max_amplitude: 0.0099',
                    'files_checked: 6',
                    'files_ignored: 0',
                    'files_with_gaps: 4',
                    ' - 01-gap.flac',
                    ' - 03-gap.flac',
                    ' - 04-gap.flac',
                    ' - 06-gap.flac',
                    'file_joined: 01-gap__GAPLESS.flac',
                    ' - 01-gap.flac',
                    ' - 02-silence.flac',
                    'file_joined: 03-gap__GAPLESS.flac',
                    ' - 03-gap.flac',
                    ' - 04-gap.flac',
                    ' - 05-silence.flac']

        parser = buildparser.build_parser()
        options = parser.parse_args(['-j', '-p', './tests/audio/join'])

        gapcheck.gapcheck(options)

        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")
        # because stdout is an StringIO instance
        output = sys.stdout.getvalue().strip().replace('\\', '/').split('\n')

        for i in range(len(output)):
            if 'directory' in output[i] or 'date' in output[i]:
                continue
            else:
                self.assertEqual(output[i], expected[i])

        # check si el fichero ./test/audio/gapcheck.log existe
        self.assertTrue(os.path.isfile('./tests/audio/join/gapcheck.log'))

    def test_gapcheck_join_last_songs_with_gap(self):
        """ Las n ultimas canciones con gap """

        # No es posible testear el directorio y la fecha...
        expected = ['directory: null',
                    'date: null',
                    'extension: flac',
                    'sox_last_seconds: 0.2',
                    'sox_max_amplitude: 0.0099',
                    'files_checked: 2',
                    'files_ignored: 0',
                    'files_with_gaps: 2',
                    ' - 01-gap.flac',
                    ' - 02-gap.flac',
                    'file_joined: 01-gap__GAPLESS.flac',
                    ' - 01-gap.flac',
                    ' - 02-gap.flac']

        parser = buildparser.build_parser()
        options = parser.parse_args(['-j', '-p', './tests/audio/other'])

        gapcheck.gapcheck(options)

        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")
        # because stdout is an StringIO instance
        output = sys.stdout.getvalue().strip().replace('\\', '/').split('\n')

        for i in range(len(output)):
            if 'directory' in output[i] or 'date' in output[i]:
                continue
            else:
                self.assertEqual(output[i], expected[i])

        # check si el fichero ./test/audio/gapcheck.log existe
        self.assertTrue(os.path.isfile('./tests/audio/other/gapcheck.log'))

        # leemos los tags del fichero destino
        filedest = './tests/audio/other/01-gap__GAPLESS.flac'
        tags = FLAC(filedest)

        # 3. revisamos TODOS los tags
        self.assertEqual(tags['gapless_join'], ['2'])
        self.assertEqual(tags['gapless_last_discnumber'], ['1'])
        self.assertEqual(tags['gapless_last_track'], ['1'])
