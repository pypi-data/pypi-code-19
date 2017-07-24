"""
Wrapper functions for PythonMagick for functional programming
"""

import PythonMagick as pm

def loadImg(path):
    """Load image on path, then return a PythonMagick Image object"""
    print("Load from {}".format(path))
    return pm.Image(path)


def saveImg(path, img):
    """Save image object to path"""
    print("Save to {}\n".format(path))
    img.write(path)


def scaleImg(width, height, img, keepRatio=False):
    """Scale image to given width and height if keep aspect ratio is True
    """
    ignoreAspectMark = "!" if keepRatio is False else ""
    transformStr = "{}{}x{}".format(ignoreAspectMark, width, height)
    print("Scale to {}".format(transformStr))
    img.transform(transformStr)
    return img
