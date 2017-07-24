# Separate utility functions to make the main module scope clean

import re
import os
import magic

# Load mime type defining magic number associations for later use
m = magic.open(magic.MIME)
m.load()


def unMark(opts):
    newOptDict = {}
    """Remove docopt specific markings from the options like '--' or '< >'"""
    for k, v in opts.items():
        newKey = re.sub("(^--|^<|>$)", "", k)
        newOptDict[newKey] = v
    return newOptDict


def isImageFile(path):
    """Return True if file on path is an image
    according to its MIME type, false otherwise"""
    currentMime = m.file(path)
    acceptedMimeTypes = ["image/jpeg",
                         "image/png",
                         "image/gif"]
    for mimeType in acceptedMimeTypes:
        if mimeType in currentMime:
            return True
    return False


# validator functions
def isDirReadable(path, msg):
    if not os.access(path, os.R_OK):
        raise OSError(msg)


def isDirWriteable(path, msg):
    if not os.access(path, os.W_OK):
        raise OSError(msg)


def isValidRatio(x):
    if not isinstance(x, float):
        raise TypeError()
    if x < 0:
        raise ValueError("Ratio must be a positive number")
    if x > 1:
        print("Warning: A ratio larger than 1 works, but sensless.")


def isValidResList(resList):
    if not isinstance(resList, list):
        raise TypeError("Wrong resolutions format")
    if len(resList) < 1:
        raise TypeError("Wrong resolutions format")

    for res in resList:
        if not isinstance(res, int):
            raise TypeError("Wrong resolutions format")
