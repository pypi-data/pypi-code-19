from __future__ import unicode_literals

import imghdr
import os
import unittest
import warnings

from PIL import Image
from random import randint
from tempfile import NamedTemporaryFile
from unittest.mock import *

import tecplot as tp
from tecplot.exception import *
from tecplot.constant import *
from tecplot.export import save_jpeg, save_png, save_tiff
from tecplot.tecutil import sv
from tecplot.layout import Frame

from .. import patch_tecutil, closed_tempfile


class TestExport(unittest.TestCase):
    _TESTING_WIDTH = 32

    def setUp(self):
        warnings.simplefilter('ignore')
        self.export_formats = {
            save_jpeg: ExportFormat.JPEG,
            save_png: ExportFormat.PNG,
            save_tiff: ExportFormat.TIFF
        }

    def tearDown(self):
        warnings.simplefilter('default')

    @staticmethod
    def export_setup_called_with(export_setup, sv_constant, value=None):
        #   @type export_setup: Mock
        for call_arg in export_setup.call_args_list:
            if call_arg[0][0] == sv_constant and any([
                        value is None,
                        call_arg[0][2] == value,  # d value
                        call_arg[0][3] == value]):  # i value
                return True
        return False

    def test_export_error(self):
        for export_function in self.export_formats.keys():
            with patch_tecutil('ExportSetup') as export_setup:  # type: Mock
                with patch_tecutil('Export') as export:  # type: Mock
                    export_setup.return_value = SetValueReturnCode.Ok
                    export.return_value = False
                    with self.assertRaises(TecplotSystemError):
                        export_function('abc', self._TESTING_WIDTH)

    def test_export_setup_error(self):
        for export_function in self.export_formats.keys():
            with patch_tecutil('ExportSetup') as export_setup:  # type: Mock
                with patch_tecutil('Export') as export:  # type: Mock
                    export_setup.return_value = SetValueReturnCode.AssignOpError
                    export.return_value = True
                    with self.assertRaises(TecplotSystemError):
                        export_function('abc', self._TESTING_WIDTH)

    def test_export_called(self):
        for export_function in self.export_formats.keys():
            with patch_tecutil('ExportSetup') as export_setup:  # type: Mock
                with patch_tecutil('Export') as export:  # type: Mock
                    export_setup.return_value = SetValueReturnCode.Ok
                    export.return_value = True
                    export_function('abc', self._TESTING_WIDTH)
                    self.assertEqual(export.call_count, 1)

    def test_required_arguments(self):
        for export_function in self.export_formats.keys():
            with patch_tecutil('ExportSetup') as export_setup:  # type: Mock
                with patch_tecutil('Export') as export:  # type: Mock
                    export_setup.return_value = SetValueReturnCode.Ok
                    export.return_value = True
                    export_function('abc', self._TESTING_WIDTH)
                    # export_setup
                    # should be called for file type, filename, and width
                    self.assertTrue(self.export_setup_called_with(
                        export_setup, sv.EXPORTFNAME, 'abc'))
                    self.assertTrue(self.export_setup_called_with(
                        export_setup, sv.IMAGEWIDTH, self._TESTING_WIDTH))

    def test_file_types(self):
        for export_function, export_format in self.export_formats.items():
            with patch_tecutil('ExportSetup') as export_setup:  # type: Mock
                with patch_tecutil('Export') as export:  # type: Mock
                    export_setup.return_value = SetValueReturnCode.Ok
                    export.return_value = True
                    export_function('abc', self._TESTING_WIDTH)
                    self.assertTrue(self.export_setup_called_with(
                        export_setup, sv.EXPORTFORMAT, export_format))

    def test_convert_to_256_colors(self):
        for export_function in [save_png, save_tiff]:
            with patch_tecutil('ExportSetup') as export_setup:  # type: Mock
                with patch_tecutil('Export') as export:  # type: Mock
                    export_setup.return_value = SetValueReturnCode.Ok
                    export.return_value = True
                    export_function('abc', self._TESTING_WIDTH,
                                    convert_to_256_colors=True)
                    self.assertTrue(self.export_setup_called_with(
                            export_setup, sv.CONVERTTO256COLORS))

    def test_valid_supersample(self):
        for export_function in self.export_formats.keys():
            with patch_tecutil('ExportSetup') as export_setup:  # type: Mock
                with patch_tecutil('Export') as export:  # type: Mock
                    export_setup.return_value = SetValueReturnCode.Ok
                    export.return_value = True
                    export_function('abc', 300, supersample=2)
                    self.assertTrue(self.export_setup_called_with(
                            export_setup, sv.USESUPERSAMPLEANTIALIASING, True))
                    self.assertTrue(self.export_setup_called_with(
                            export_setup, sv.SUPERSAMPLEFACTOR, 2))

    def test_invalid_supersample(self):
        for export_function in self.export_formats.keys():
            with patch_tecutil('ExportSetup') as export_setup:  # type: Mock
                with patch_tecutil('Export') as export:  # type: Mock
                    export_setup.return_value = SetValueReturnCode.Ok
                    export.return_value = True
                    with self.assertRaises(TecplotSystemError):
                        export_function('abc', self._TESTING_WIDTH,
                                        supersample=1)
                    with self.assertRaises(TecplotSystemError):
                        export_function('abc', self._TESTING_WIDTH,
                                        supersample=19)

    def test_invalid_tiff_depth(self):
            with patch_tecutil('ExportSetup') as export_setup:  # type: Mock
                export_setup.return_value = SetValueReturnCode.Ok
                for depth in [2, 3, 5, 7, 9]:
                    with self.assertRaises(TecplotSystemError):
                        save_tiff('abc', self._TESTING_WIDTH,
                                  gray_scale_depth=depth)

    def test_use_screen_width_if_image_width_is_none(self):
        for export_function, export_format in self.export_formats.items():
            with patch_tecutil('ExportSetup') as export_setup:  # type: Mock
                with patch_tecutil('Export') as export:  # type: Mock
                    default_width = 314
                    with patch_tecutil('GetDefaultExportImageWidth') as (
                            get_default_export_image_width):  # type: Mock
                        get_default_export_image_width.return_value = (
                            default_width)
                        export_setup.return_value = SetValueReturnCode.Ok
                        export.return_value = True
                        export_function('abc', width=None)
                        self.assertTrue(self.export_setup_called_with(
                            export_setup, sv.IMAGEWIDTH, default_width))

    def test_export_region_is_frame(self):
        for export_function in self.export_formats.keys():
            with patch_tecutil('ExportSetup') as export_setup:  # type: Mock
                with patch_tecutil('Export') as export:  # type: Mock
                    export_setup.return_value = SetValueReturnCode.Ok
                    export.return_value = True
                    export_function('abc', self._TESTING_WIDTH,
                                    region=tp.active_frame())
                    self.assertTrue(self.export_setup_called_with(
                            export_setup, sv.EXPORTREGION,
                            ExportRegion.CurrentFrame))

    def test_export_region_is_not_frame(self):
        for export_function in self.export_formats.keys():
            with patch_tecutil('ExportSetup') as export_setup:  # type: Mock
                with patch_tecutil('Export') as export:  # type: Mock
                    export_setup.return_value = SetValueReturnCode.Ok
                    export.return_value = True
                    export_function('abc', self._TESTING_WIDTH,
                                    region=ExportRegion.AllFrames)
                    self.assertTrue(self.export_setup_called_with(
                        export_setup, sv.EXPORTREGION, ExportRegion.AllFrames))

    def test_valid_jpeg_quality(self):
        with patch_tecutil('ExportSetup') as export_setup:  # type: Mock
            with patch_tecutil('Export') as export:  # type: Mock
                export_setup.return_value = SetValueReturnCode.Ok
                export.return_value = True
                save_jpeg('abc', self._TESTING_WIDTH, quality=75)
                self.assertTrue(self.export_setup_called_with(
                    export_setup, sv.QUALITY, 75.0))

    def test_jpeg_quality_clamping(self):
        with patch_tecutil('ExportSetup') as export_setup:  # type: Mock
            with patch_tecutil('Export') as export:  # type: Mock
                export_setup.return_value = SetValueReturnCode.Ok
                export.return_value = True
                save_jpeg('abc', self._TESTING_WIDTH, quality=0)
                self.assertTrue(self.export_setup_called_with(
                    export_setup, sv.QUALITY, 1.0))
                save_jpeg('abc', self._TESTING_WIDTH, quality=101)
                self.assertTrue(self.export_setup_called_with(
                    export_setup, sv.QUALITY, 100.0))

    def test_save_real_file(self):
        tp.new_layout()
        for export_function in self.export_formats.keys():
            with closed_tempfile('.tmp') as fname:
                region = [ExportRegion.CurrentFrame, ExportRegion.AllFrames,
                          ExportRegion.WorkArea][randint(0, 2)]
                # Use a very small width for speed
                export_function(fname, width=self._TESTING_WIDTH,
                                region=region,
                                supersample=2)

    def test_save_real_file_with_frame_object(self):
        tp.new_layout()
        for export_function in self.export_formats.keys():
            frame = tp.active_frame()
            with closed_tempfile('.tmp') as fname:
                export_function(fname, width=self._TESTING_WIDTH,
                                region=frame)

    def test_save_real_file_with_256_colors(self):
        tp.new_layout()
        for export_function, export_format in self.export_formats.items():
            if export_format != ExportFormat.JPEG:
                with closed_tempfile('.tmp') as fname:
                    export_function(fname, width=self._TESTING_WIDTH,
                                    convert_to_256_colors=True)

    def test_save_real_file_jpeg_options(self):
        tp.new_layout()
        encoding = [JPEGEncoding.Progressive,
                    JPEGEncoding.Standard][randint(0, 1)]
        with closed_tempfile('.tmp') as fname:
            save_jpeg(fname, self._TESTING_WIDTH, quality=50,
                      encoding=encoding)

    def test_save_real_file_tiff_options(self):
        tp.new_layout()
        byte_order = [TIFFByteOrder.Intel, TIFFByteOrder.Motorola
                      ][randint(0, 1)]
        gray_scale_depth = [None, 0, 1, 4, 8][randint(0, 4)]

        with closed_tempfile('.tmp') as fname:
            save_tiff(fname, self._TESTING_WIDTH,
                      byte_order=byte_order,
                      gray_scale_depth=gray_scale_depth)

    def test_save_real_file_with_screenwidth(self):
        tp.new_layout()
        export_functions = [K for K in self.export_formats.keys()]
        export_function = export_functions[
                randint(0, len(export_functions)-1)]
        region = [ExportRegion.CurrentFrame,
                  ExportRegion.AllFrames,
                  ExportRegion.WorkArea][randint(0, 2)]
        with closed_tempfile('.tmp') as fname:
            export_function(fname, width=None, region=region)

    def test_save_jpeg_saves_jpg(self):
        tp.new_layout()
        with closed_tempfile('.jpg') as fname:
            save_jpeg(fname, self._TESTING_WIDTH)
            self.assertEqual(imghdr.what(fname), 'jpeg')

    def test_save_png_saves_png(self):
        tp.new_layout()
        with closed_tempfile('.png') as fname:
            save_png(fname, self._TESTING_WIDTH)
            self.assertEqual(imghdr.what(fname), 'png')

    def test_save_tiff_saves_tiff(self):
        tp.new_layout()
        with closed_tempfile('.tiff') as fname:
            save_tiff(fname, self._TESTING_WIDTH)
            self.assertEqual(imghdr.what(fname), 'tiff')

    def test_save_ps(self):
        tp.new_layout()
        with closed_tempfile('.ps') as fname:
            tp.export.save_ps(fname)
            with Image.open(fname) as img:
                self.assertEqual(img.format, 'EPS')

if __name__ == '__main__':
    from .. import main
    main()
