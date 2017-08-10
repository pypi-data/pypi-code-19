#!/usr/bin/env python3
"Turn images into 120x180 JPEG thumbnails"

import os
import sys
from PIL import Image

_THUMBSIZE = (120, 180)


def thumbnail(infile):
    "Takes a file name and turns it into a 120x180 JPG"
    img = Image.open(infile).resize(_THUMBSIZE)
    img.mode = "RGB"
    outfile, _ = os.path.splitext(infile)
    img.save(outfile + ".jpg", quality=100)


def main():
    """Main function.
    Turns all images, passed through sys.argv, into thumbnails.
    """
    for inputfile in sys.argv[1:]:
        thumbnail(inputfile)
