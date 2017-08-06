import os


def walkdirectory(directory):
    fileslist = list()
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            checkfile = os.path.join(dirpath, filename)
            if os.path.isfile(checkfile):
                fileslist.append(checkfile)
    return fileslist