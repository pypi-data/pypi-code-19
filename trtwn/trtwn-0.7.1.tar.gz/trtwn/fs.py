import os

def purename(filename):
    return os.path.splitext(os.path.basename(filename))[0]

def changeExtension(filepath, ext):
    if not ext.startswith("."):
        ext = "." + ext
    return os.path.splitext(filepath)[0] + ext
