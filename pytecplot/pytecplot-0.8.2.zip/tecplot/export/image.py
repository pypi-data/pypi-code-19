from ..tecutil import _tecutil, lock
from .. constant import *
from ..exception import TecplotSystemError
import logging
from tecplot.tecutil import sv
from ..layout import frame

log = logging.getLogger(__name__)


def _set_export_attribute(sv_constant, value):
    i_value, d_value = (0, value) if isinstance(value, float) else (value, 0.0)

    result = _tecutil.ExportSetup(sv_constant, None, d_value, i_value)
    if result not in [SetValueReturnCode.Ok, SetValueReturnCode.DuplicateValue]:
        raise TecplotSystemError(
            'Invalid {} value: {}'.format(sv_constant, value))


def _reset_export_setup_to_defaults():

    # See the Tecplot scripting guide for default values used below.
    _set_export_attribute(sv.EXPORTREGION, ExportRegion.CurrentFrame)
    _set_export_attribute(sv.CONVERTTO256COLORS, False)
    _set_export_attribute(sv.IMAGEWIDTH, 512)
    _set_export_attribute(sv.USESUPERSAMPLEANTIALIASING, False)
    _set_export_attribute(sv.SUPERSAMPLEFACTOR, 3)
    _set_export_attribute(sv.GRAYSCALEDEPTH, 8)
    _set_export_attribute(sv.TIFFBYTEORDER, TIFFByteOrder.Intel)
    _set_export_attribute(sv.QUALITY, 75.0)


def _setup_common_attributes(export_format, filename, width, region, supersample,
                             convert_to_256_colors):

    _set_export_attribute(sv.EXPORTFNAME, filename)

    final_region = ExportRegion.CurrentFrame if isinstance(
        region, frame.Frame) or region is None else region

    # None or 0 width implies "use screen width".
    # The screen width is calculated with a TecUtil call.

    final_width = _tecutil.GetDefaultExportImageWidth(
        export_format.value, final_region.value) if not width else width

    _set_export_attribute(sv.IMAGEWIDTH, final_width)

    _set_export_attribute(sv.EXPORTFORMAT, export_format)

    if convert_to_256_colors:
        _set_export_attribute(sv.CONVERTTO256COLORS, True)

    if region:
        _set_export_attribute(sv.EXPORTREGION, final_region)

    if supersample:
        _set_export_attribute(sv.USESUPERSAMPLEANTIALIASING, True)
        if not (2 <= supersample <= 16):
            raise TecplotSystemError('supersample must be between 2 and 16')

        _set_export_attribute(sv.SUPERSAMPLEFACTOR, supersample)


def _do_export(export_type, filename, width, region, supersample,
               convert_to_256_colors, additional_attributes):

    def internal_export():
        _setup_common_attributes(export_format=export_type, filename=filename,
                                 width=width, region=region,
                                 supersample=supersample,
                                 convert_to_256_colors=convert_to_256_colors)

        for attribute in additional_attributes:
            if attribute[1] is not None:
                if attribute[0] == sv.GRAYSCALEDEPTH and attribute[1] not in [
                                    0, 1, 4, 8]:
                    raise TecplotSystemError('Gray Scale Depth must be one of '
                                             '[0, 1, 4, 8]')
                _set_export_attribute(attribute[0], attribute[1])

        if not _tecutil.Export(append=False):
            raise TecplotSystemError

    try:
        _reset_export_setup_to_defaults()

        if isinstance(region, frame.Frame):
            with region.activated():
                internal_export()
        else:
            internal_export()

    except TecplotSystemError as e:
        raise TecplotSystemError('Could not export image "{}" : {}'
                                 .format(filename, e))


@lock()
def save_jpeg(filename, width, region=None, supersample=None, encoding=None,
              quality=None):
    """Save a `JPEG image
    <https://en.wikipedia.org/wiki/JPEG>`_.

    Parameters:
        filename (`string <str>`): |export_filename_description|

        width (`integer <int>`): |export_width_description|

        region (`frame <Frame>` or `ExportRegion`, optional): |export_region_description|

        supersample (`integer <int>`, optional): |export_supersample_description|

        quality (`integer <int>` 1-100, optional)
            Select the quality of JPEG image.
            Higher quality settings produce larger files and better
            looking export images. Lower quality settings produce smaller files.
            For best results, use a quality setting of **75** or higher.
            (default: **75**)

        encoding (`JPEGEncoding`, optional)
            Encoding method for the JPEG file.

            Encoding may be one of the following:
                * `JPEGEncoding.Standard`
                    Creates a JPEG which downloads one line at a time,
                    starting at the top line.
                * `JPEGEncoding.Progressive`
                    Creates a JPEG image that can be displayed with
                    a "fade in" effect in a browser.
                    This is sometimes useful when viewing the JPEG in a
                    browser with a slow connection, since it allows
                    an approximation of the JPEG to be drawn immediately,
                    and the browser does not have to wait for the entire
                    image to download.

                (default: `JPEGEncoding.Standard`)

    Raises:
        `TecplotSystemError`: The image could not be saved due to a
            file I/O error or invalid attribute.

    .. note::
        |export_general_info|

    Create a new `frame <Frame>` and save a JPEG image of the frame
    with quality **50** and supersampling::

        >>> import tecplot
        >>> frame = tecplot.active_page().add_frame()
        >>> tecplot.load_layout('mylayout.lay')
        >>> tecplot.export.save_jpeg('image.jpeg', width=600, supersample=2,
        >>>                         region=frame,
        >>>                         quality=50)
    """

    # clamp quality to 1-100 and divide by 100
    final_quality = float(max(1, min(quality, 100))
                          ) if quality is not None else None

    _do_export(export_type=ExportFormat.JPEG, filename=filename, width=width,
               region=region, supersample=supersample,
               convert_to_256_colors=None,
               additional_attributes=[(sv.QUALITY, final_quality),
                                      (sv.JPEGENCODING, encoding)])

    log.info('JPEG image file created: ' + filename)


@lock()
def save_tiff(filename, width, region=None, supersample=None,
              convert_to_256_colors=None, gray_scale_depth=None,
              byte_order=None):
    """Save a `TIFF image
    <https://en.wikipedia.org/wiki/TIFF>`_.

    Parameters:
        filename (`string <str>`): |export_filename_description|

        width (`integer <int>`): |export_width_description|

        region (`frame <Frame>` or `ExportRegion`, optional): |export_region_description|

        supersample (`integer <int>`, optional): |export_supersample_description|

        convert_to_256_colors (`Boolean <bool>`, optional): |export_convert256_description|

        gray_scale_depth (`integer <int>`, optional)
            Export a gray-scale TIFF.
            The ``gray_scale_depth`` parameter may be
            set to a depth of **1-8**

            ``gray_scale_depth`` specifies the
            number of shades of gray by how many bits of gray scale
            information is used per pixel.
            The larger the number of bits per pixel, the larger the
            resulting file.

            Options are:
                * **0**: On/Off
                    One bit per pixel using an on/off strategy.
                    All background pixels are made white (on),
                    and all foreground pixels, black (off).
                    This setting creates small files and is
                    good for images with lots of background, such as line
                    plots and contour lines.
                * **1**: 1 Bit per Pixel
                    One bit per pixel using gray scale values of
                    pixels to determine black or white.
                    Those pixels that are more than 50 percent gray are
                    black; the rest are white. This setting creates small
                    files that might be useful for a rough draft
                    or a preview image.
                * **4**: 4 Bits per Pixel
                    Four bits per pixel resulting
                    in sixteen levels of gray scale. This setting
                    generates fairly small image files with a
                    fair number of gray levels.
                    This setting works well for most preview image purposes.
                * **8**:  8 Bits per Pixel
                    Eight bits per pixel resulting in 256 levels of gray.
                    This setting is useful for full image
                    representation, but the files generated by this
                    setting can be large.

                (default: `None`)

        byte_order (`TIFFByteOrder`, optional)
            Specify the byte order (Intel or Motorola) of the TIFF image.
            (Default: `TIFFByteOrder.Intel`)


    Raises:
        `TecplotSystemError`: The image could not be saved due to a
            file I/O error or invalid attribute.

    .. note::
        |export_general_info|

    Save a 4-bit gray scale TIFF image of the entire workspace with supersampling::

        >>> import tecplot
        >>> from tecplot.constant import ExportRegion
        >>> tecplot.load_layout('mylayout.lay')
        >>> tecplot.export.save_tiff('image.tiff', width=600, supersample=2,
        >>>                         region=ExportRegion.WorkArea,
        >>>                         gray_scale_depth=4)
    """

    _do_export(export_type=ExportFormat.TIFF, filename=filename, width=width,
               region=region, supersample=supersample,
               convert_to_256_colors=convert_to_256_colors,
               additional_attributes=[(sv.TIFFBYTEORDER, byte_order),
                                      (sv.GRAYSCALEDEPTH, gray_scale_depth)])

    log.info('TIFF image file created: '+filename)


@lock()
def save_png(filename, width, region=None, supersample=None,
             convert_to_256_colors=None):
    """Save a `PNG image
    <https://en.wikipedia.org/wiki/Portable_Network_Graphics>`_.

    Parameters:
        filename (`string <str>`): |export_filename_description|

        width (`integer <int>`):  |export_width_description|

        region (`frame <Frame>` or `ExportRegion`, optional): |export_region_description|

        supersample (`integer <int>`, optional): |export_supersample_description|

        convert_to_256_colors (`Boolean <bool>`, optional): |export_convert256_description|

    Raises:
        `TecplotSystemError`: The image could not be saved due to a
            file I/O error or invalid attribute.

    .. note::
        |export_general_info|

    Save a PNG image of the entire workspace with supersampling::

        >>> import tecplot
        >>> from tecplot.constant import ExportRegion
        >>> tecplot.load_layout('mylayout.lay')
        >>> tecplot.export.save_png('image.png', width=600, supersample=2,
        >>>                         region=ExportRegion.WorkArea)

    """
    _do_export(export_type=ExportFormat.PNG, filename=filename, width=width,
               region=region, supersample=supersample,
               convert_to_256_colors=convert_to_256_colors,
               additional_attributes=[])

    log.info('PNG image file created: '+filename)


@lock()
def save_ps(filename):
    """Save a `PostScript image <https://en.wikipedia.org/wiki/PostScript>`_.

    Parameters:
        filename (`string <str>`): |export_filename_description|

    Raises:
        `TecplotSystemError`: The image could not be saved due to a
            file I/O error or invalid attribute.
    """
    _do_export(ExportFormat.PS, filename, None, None, None, None, [])
    log.info('PostScript image file created: ' + filename)
