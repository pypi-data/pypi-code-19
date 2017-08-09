# -*- coding: utf-8 -*-

import unittest
import sys
import os
import pathlib
import shutil
from gapcheck import gapcheck
from gapcheck import gap
from gapcheck import buildparser



class TestGapCheck(unittest.TestCase):
    """ Test GapCheck """

    def setUp(self):
        """ Limpieza y generación de ficheros necesarios """
        # limpieza por si hubiera ficheros mal

        files_to_delete = ['./tests/audio/gap/gapcheck.log',
                           './tests/audio/gap/ignore/gapcheck.log',
                           './tests/audio/gap/gap_GAPLESS.flac']

        for ftd in files_to_delete:
            if os.path.isfile(ftd):
                os.remove(ftd)

        files_to_mv = [['./tests/audio/gap/__backup/__BACKUP_gap.flac_bck',
                        './tests/audio/gap/gap.flac'],
                       ['./tests/audio/gap/__backup/__BACKUP_silence.flac_bck',
                        './tests/audio/gap/silence.flac']]

        for ftr in files_to_mv:
            if os.path.isfile(ftr[0]):
                os.rename(ftr[0], ftr[1])

        dirs_to_delete = ['./tests/audio/gap/__backup']

        for dtd in dirs_to_delete:
            if os.path.isdir(dtd):
                shutil.rmtree(dtd)

        # ... y creo los que necesito
        pathlib.Path('./tests/audio/gap/ignore/gapcheck.log').touch()

    def test_silent(self):
        finput = './tests/audio/gap/silence.flac'
        self.assertFalse(gap.check_if_gap(finput, 0.2, 0.0099))

    def test_gap(self):
        finput = './tests/audio/gap/gap.flac'
        self.assertTrue(gap.check_if_gap(finput, 0.2, 0.0099))

    def test_ignore_files(self):
        finput = './tests/audio/gap/ignore/ignore.flac'
        self.assertTrue(gapcheck.check_if_ignore(finput))

    def test_argparser(self):

        parser = buildparser.build_parser()
        options = parser.parse_args(['-e', 'FLAC', '-p', 'PATH', '-f'])

        self.assertEqual('FLAC', options.extension)
        self.assertEqual('PATH', options.path)
        self.assertEqual(0.2, options.seconds)
        self.assertEqual(0.0099, options.max_amplitude)
        self.assertTrue(options.force_analyze)

        options = parser.parse_args(['-s', '4', '-a', '1.5'])

        self.assertEqual('flac', options.extension)
        self.assertEqual('.', options.path)
        self.assertEqual(4.0, options.seconds)
        self.assertEqual(1.5, options.max_amplitude)
        self.assertFalse(options.force_analyze)

    def test_gapcheck(self):

        # No es posible testear el directorio y la fecha...
        expected = ['directory: null',
                    'date: null',
                    'extension: flac',
                    'sox_last_seconds: 0.2',
                    'sox_max_amplitude: 0.0099',
                    'files_checked: 2',
                    'files_ignored: 0',
                    'files_with_gaps: 1',
                    ' - gap.flac',
                    'directory: null',
                    'date: null',
                    'extension: flac',
                    'sox_last_seconds: 0.2',
                    'sox_max_amplitude: 0.0099',
                    'files_checked: 1',
                    'files_ignored: 1',
                    'files_with_gaps: 0',
                    'directory: null',
                    'date: null',
                    'extension: flac',
                    'sox_last_seconds: 0.2',
                    'sox_max_amplitude: 0.0099',
                    'files_checked: 1',
                    'files_ignored: 1',
                    'files_with_gaps: 0']

        parser = buildparser.build_parser()
        options = parser.parse_args(['-e', 'flac', '-p', './tests/audio/gap'])

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

        # check si el fichero ./test/audio/gap/gapcheck.log existe
        self.assertTrue(os.path.isfile('./tests/audio/gap/gapcheck.log'))


    def test_gapcheck_force(self):

        # No es posible testear el directorio y la fecha...
        expected = ['directory: null',
                    'date: null',
                    'extension: flac',
                    'sox_last_seconds: 0.2',
                    'sox_max_amplitude: 0.0099',
                    'files_checked: 2',
                    'files_ignored: 0',
                    'files_with_gaps: 1',
                    ' - gap.flac',
                    'directory: null',
                    'date: null',
                    'extension: flac',
                    'sox_last_seconds: 0.2',
                    'sox_max_amplitude: 0.0099',
                    'files_checked: 1',
                    'files_ignored: 0',
                    'files_with_gaps: 0',
                    'directory: null',
                    'date: null',
                    'extension: flac',
                    'sox_last_seconds: 0.2',
                    'sox_max_amplitude: 0.0099',
                    'files_checked: 1',
                    'files_ignored: 0',
                    'files_with_gaps: 0']

        parser = buildparser.build_parser()
        options = parser.parse_args(['-p', './tests/audio/gap', '-f'])

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

        # check si el fichero ./test/audio/gap/gapcheck.log existe
        self.assertTrue(os.path.isfile('./tests/audio/gap/gapcheck.log'))

    def test_gapcheck_ogg(self):

        # No es posible testear el directorio y la fecha...
        expected = ['directory: null',
                    'date: null',
                    'extension: ogg',
                    'sox_last_seconds: 0.2',
                    'sox_max_amplitude: 0.0099',
                    'files_checked: 2',
                    'files_ignored: 0',
                    'files_with_gaps: 1',
                    ' - gap.ogg',
                    'directory: null',
                    'date: null',
                    'extension: ogg',
                    'sox_last_seconds: 0.2',
                    'sox_max_amplitude: 0.0099',
                    'files_checked: 1',
                    'files_ignored: 1',
                    'files_with_gaps: 0',
                    'directory: null',
                    'date: null',
                    'extension: ogg',
                    'sox_last_seconds: 0.2',
                    'sox_max_amplitude: 0.0099',
                    'files_checked: 1',
                    'files_ignored: 1',
                    'files_with_gaps: 0']

        parser = buildparser.build_parser()
        options = parser.parse_args(['-e', 'ogg', '-p', './tests/audio/gap'])

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

        # check si el fichero ./test/audio/gap/gapcheck.log existe
        self.assertTrue(os.path.isfile('./tests/audio/gap/gapcheck.log'))
