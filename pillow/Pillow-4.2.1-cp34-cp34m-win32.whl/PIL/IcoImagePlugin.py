#
# The Python Imaging Library.
# $Id$
#
# Windows Icon support for PIL
#
# History:
#       96-05-27 fl     Created
#
# Copyright (c) Secret Labs AB 1997.
# Copyright (c) Fredrik Lundh 1996.
#
# See the README file for information on usage and redistribution.
#

# This plugin is a refactored version of Win32IconImagePlugin by Bryan Davis
# <casadebender@gmail.com>.
# https://code.google.com/archive/p/casadebender/wikis/Win32IconImagePlugin.wiki
#
# Icon format references:
#   * https://en.wikipedia.org/wiki/ICO_(file_format)
#   * https://msdn.microsoft.com/en-us/library/ms997538.aspx


import struct
from io import BytesIO

from . import Image, ImageFile, BmpImagePlugin, PngImagePlugin
from ._binary import i8, i16le as i16, i32le as i32
from math import log, ceil

__version__ = "0.1"

#
# --------------------------------------------------------------------

_MAGIC = b"\0\0\1\0"


def _save(im, fp, filename):
    fp.write(_MAGIC)  # (2+2)
    sizes = im.encoderinfo.get("sizes",
                               [(16, 16), (24, 24), (32, 32), (48, 48),
                                (64, 64), (128, 128), (256, 256)])
    width, height = im.size
    sizes = filter(lambda x: False if (x[0] > width or x[1] > height or
                                       x[0] > 256 or x[1] > 256) else True,
                   sizes)
    sizes = list(sizes)
    fp.write(struct.pack("<H", len(sizes)))  # idCount(2)
    offset = fp.tell() + len(sizes)*16
    for size in sizes:
        width, height = size
        # 0 means 256
        fp.write(struct.pack("B", width if width < 256 else 0))  # bWidth(1)
        fp.write(struct.pack("B", height if height < 256 else 0))  # bHeight(1)
        fp.write(b"\0")  # bColorCount(1)
        fp.write(b"\0")  # bReserved(1)
        fp.write(b"\0\0")  # wPlanes(2)
        fp.write(struct.pack("<H", 32))  # wBitCount(2)

        image_io = BytesIO()
        tmp = im.copy()
        tmp.thumbnail(size, Image.LANCZOS)
        tmp.save(image_io, "png")
        image_io.seek(0)
        image_bytes = image_io.read()
        bytes_len = len(image_bytes)
        fp.write(struct.pack("<I", bytes_len))  # dwBytesInRes(4)
        fp.write(struct.pack("<I", offset))  # dwImageOffset(4)
        current = fp.tell()
        fp.seek(offset)
        fp.write(image_bytes)
        offset = offset + bytes_len
        fp.seek(current)


def _accept(prefix):
    return prefix[:4] == _MAGIC


class IcoFile(object):
    def __init__(self, buf):
        """
        Parse image from file-like object containing ico file data
        """

        # check magic
        s = buf.read(6)
        if not _accept(s):
            raise SyntaxError("not an ICO file")

        self.buf = buf
        self.entry = []

        # Number of items in file
        self.nb_items = i16(s[4:])

        # Get headers for each item
        for i in range(self.nb_items):
            s = buf.read(16)

            icon_header = {
                'width': i8(s[0]),
                'height': i8(s[1]),
                'nb_color': i8(s[2]),  # No. of colors in image (0 if >=8bpp)
                'reserved': i8(s[3]),
                'planes': i16(s[4:]),
                'bpp': i16(s[6:]),
                'size': i32(s[8:]),
                'offset': i32(s[12:])
            }

            # See Wikipedia
            for j in ('width', 'height'):
                if not icon_header[j]:
                    icon_header[j] = 256

            # See Wikipedia notes about color depth.
            # We need this just to differ images with equal sizes
            icon_header['color_depth'] = (icon_header['bpp'] or
                                          (icon_header['nb_color'] != 0 and
                                           ceil(log(icon_header['nb_color'],
                                                    2))) or 256)

            icon_header['dim'] = (icon_header['width'], icon_header['height'])
            icon_header['square'] = (icon_header['width'] *
                                     icon_header['height'])

            self.entry.append(icon_header)

        self.entry = sorted(self.entry, key=lambda x: x['color_depth'])
        # ICO images are usually squares
        # self.entry = sorted(self.entry, key=lambda x: x['width'])
        self.entry = sorted(self.entry, key=lambda x: x['square'])
        self.entry.reverse()

    def sizes(self):
        """
        Get a list of all available icon sizes and color depths.
        """
        return {(h['width'], h['height']) for h in self.entry}

    def getimage(self, size, bpp=False):
        """
        Get an image from the icon
        """
        for (i, h) in enumerate(self.entry):
            if size == h['dim'] and (bpp is False or bpp == h['color_depth']):
                return self.frame(i)
        return self.frame(0)

    def frame(self, idx):
        """
        Get an image from frame idx
        """

        header = self.entry[idx]

        self.buf.seek(header['offset'])
        data = self.buf.read(8)
        self.buf.seek(header['offset'])

        if data[:8] == PngImagePlugin._MAGIC:
            # png frame
            im = PngImagePlugin.PngImageFile(self.buf)
        else:
            # XOR + AND mask bmp frame
            im = BmpImagePlugin.DibImageFile(self.buf)

            # change tile dimension to only encompass XOR image
            im.size = (im.size[0], int(im.size[1] / 2))
            d, e, o, a = im.tile[0]
            im.tile[0] = d, (0, 0) + im.size, o, a

            # figure out where AND mask image starts
            mode = a[0]
            bpp = 8
            for k, v in BmpImagePlugin.BIT2MODE.items():
                if mode == v[1]:
                    bpp = k
                    break

            if 32 == bpp:
                # 32-bit color depth icon image allows semitransparent areas
                # PIL's DIB format ignores transparency bits, recover them.
                # The DIB is packed in BGRX byte order where X is the alpha
                # channel.

                # Back up to start of bmp data
                self.buf.seek(o)
                # extract every 4th byte (eg. 3,7,11,15,...)
                alpha_bytes = self.buf.read(im.size[0] * im.size[1] * 4)[3::4]

                # convert to an 8bpp grayscale image
                mask = Image.frombuffer(
                    'L',            # 8bpp
                    im.size,        # (w, h)
                    alpha_bytes,    # source chars
                    'raw',          # raw decoder
                    ('L', 0, -1)    # 8bpp inverted, unpadded, reversed
                )
            else:
                # get AND image from end of bitmap
                w = im.size[0]
                if (w % 32) > 0:
                    # bitmap row data is aligned to word boundaries
                    w += 32 - (im.size[0] % 32)

                # the total mask data is
                # padded row size * height / bits per char

                and_mask_offset = o + int(im.size[0] * im.size[1] *
                                          (bpp / 8.0))
                total_bytes = int((w * im.size[1]) / 8)

                self.buf.seek(and_mask_offset)
                mask_data = self.buf.read(total_bytes)

                # convert raw data to image
                mask = Image.frombuffer(
                    '1',            # 1 bpp
                    im.size,        # (w, h)
                    mask_data,      # source chars
                    'raw',          # raw decoder
                    ('1;I', int(w/8), -1)  # 1bpp inverted, padded, reversed
                )

                # now we have two images, im is XOR image and mask is AND image

            # apply mask image as alpha channel
            im = im.convert('RGBA')
            im.putalpha(mask)

        return im


##
# Image plugin for Windows Icon files.

class IcoImageFile(ImageFile.ImageFile):
    """
    PIL read-only image support for Microsoft Windows .ico files.

    By default the largest resolution image in the file will be loaded. This
    can be changed by altering the 'size' attribute before calling 'load'.

    The info dictionary has a key 'sizes' that is a list of the sizes available
    in the icon file.

    Handles classic, XP and Vista icon formats.

    This plugin is a refactored version of Win32IconImagePlugin by Bryan Davis
    <casadebender@gmail.com>.
    https://code.google.com/archive/p/casadebender/wikis/Win32IconImagePlugin.wiki
    """
    format = "ICO"
    format_description = "Windows Icon"

    def _open(self):
        self.ico = IcoFile(self.fp)
        self.info['sizes'] = self.ico.sizes()
        self.size = self.ico.entry[0]['dim']
        self.load()

    def load(self):
        im = self.ico.getimage(self.size)
        # if tile is PNG, it won't really be loaded yet
        im.load()
        self.im = im.im
        self.mode = im.mode
        self.size = im.size

    def load_seek(self):
        # Flag the ImageFile.Parser so that it
        # just does all the decode at the end.
        pass
#
# --------------------------------------------------------------------


Image.register_open(IcoImageFile.format, IcoImageFile, _accept)
Image.register_save(IcoImageFile.format, _save)
Image.register_extension(IcoImageFile.format, ".ico")
