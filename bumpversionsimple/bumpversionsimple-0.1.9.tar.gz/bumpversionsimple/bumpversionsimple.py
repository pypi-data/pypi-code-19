#! /usr/bin/env python
import os
import sys

def main():
    versionfile = [os.path.join(root, x) for root, dirs, files in os.walk(os.getcwd()) for x in files if x == "version.py"]
    if len(versionfile) == 1:
        with open(versionfile[0]) as versionf:
            version = versionf.read().split("\"")[1]
        os.system("git commit -m 'bumping version to {}' {}".format(version, versionfile[0]))
    else:
        sys.exit("Found multiple occurences of version.py - doing nothing.")


if __name__ == '__main__':
    main()
