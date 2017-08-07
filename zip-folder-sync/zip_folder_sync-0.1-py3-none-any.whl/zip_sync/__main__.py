import sys
import os
import zipfile


def main():
    c_directory = sys.argv[1]
    c_zip = sys.argv[2]

    zip_file = zipfile.ZipFile(c_zip, 'w')
    c_infolist = zip_file.infolist()

    for subdir, dirs, files in os.walk(c_directory, topdown=False):
        for name in files:
            c_filepath = os.path.join(subdir, name)

            if c_filepath not in c_infolist:
                zip_file.write(c_directory + c_filepath, c_filepath,
                               zipfile.ZIP_DEFLATED)
