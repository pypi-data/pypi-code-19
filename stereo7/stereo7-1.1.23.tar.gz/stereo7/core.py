import version
import argparse
import inapps
import build
import os
from project import Project
import fileutils


def console():
    main()


def _version():
    print version.__version__


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', type=str, help='Path to project root', default='/Work/gushchin/td_core/projects/cult')
    parser.add_argument('-t', type=str, help='Command', default='build')
    parser.add_argument('-c', type=str, help='Build configuration (debug, release, pre-release', default='release')
    parser.add_argument('-platform', type=str, help='Build platform (windows, android, ios. (in-future: steam, os-x)', default='ios')
    parser.add_argument('-build_version', type=str, help='Build version. Can be 0 (current build version)', default='0')
    args = parser.parse_args()

    command = args.t

    fileutils.root_dir = args.p
    if not os.path.isdir(fileutils.root_dir):
        print 'Invalid path to project [{}]'.format(args.p)
        exit(-1)

    if command == 'init':
        project = Project(empty=True)
        project.create()
        exit(0)

    Project.instance = Project()

    if command == 'inapps':
        inapps.run(Project.instance.package,
                   Project.instance.name,
                   Project.instance.version,
                   Project.instance.gg_inapps)
    elif command == 'build':
        configuration = args.c
        platform = args.platform
        build_version = args.build_version
        build.run(platform,
                  configuration,
                  Project.instance.package,
                  Project.instance.version,
                  build_version)
    else:
        print 'Unknown command [{}]'.format(command)


if __name__ == '__main__':
    main()
