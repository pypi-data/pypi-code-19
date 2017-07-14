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
    parser.add_argument('-p', type=str, help='Path to project root', default='/Work/gushchin/td_core/projects/cult/')
    parser.add_argument('-c', type=str, help='Command', default='inapps')
    args = parser.parse_args()

    fileutils.root_dir = args.p
    if not os.path.isdir(fileutils.root_dir):
        print 'Invalid path to project [{}]'.format(args.p)
        exit(-1)
    project = Project()

    if args.c == 'inapps':
        inapps.run(project.package, project.name, project.version, project.gg_inapps)
    else:
        print 'Unknown command [{}]'.format(args.c)


if __name__ == '__main__':
    main()
