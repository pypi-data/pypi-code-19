import version
import argparse
import inapps
import os
from project import Project
import fileutils


def console():
    main()


def _version():
    print version.__version__


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', type=str, help='Path to project root', default='')
    parser.add_argument('-c', type=str, help='Command', default='')
    args = parser.parse_args()

    fileutils.root_dir = args.p
    if not os.path.isdir(fileutils.root_dir):
        print 'Invalid path to project [{}]'.format(args.p)
        exit(-1)

    if args.c == 'init':
        project = Project(empty=True)
        project.create()
        exit(0)

    Project.instance = Project()

    if args.c == 'inapps':
        inapps.run(Project.instance.package,
                   Project.instance.name,
                   Project.instance.version,
                   Project.instance.gg_inapps)
    else:
        print 'Unknown command [{}]'.format(args.c)


if __name__ == '__main__':
    main()
