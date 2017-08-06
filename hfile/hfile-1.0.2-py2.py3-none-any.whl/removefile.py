import os


def removefile(filepath):
    os.remove(filepath)
    return filepath