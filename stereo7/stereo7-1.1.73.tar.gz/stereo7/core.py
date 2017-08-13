import version
import arguments
import inapps
import build
import os
import sys
from project import Project
import fileutils
import validate
import compress_images
import create_sublime_project


def console():
    main()


def _version():
    print version.__version__


def main():
    parser = arguments.Parser(sys.argv)
    command = parser.command

    fileutils.root_dir = os.path.abspath(parser.root)
    if not os.path.isdir(fileutils.root_dir):
        print 'Invalid path to project [{}]'.format(parser.root)
        exit(-1)

    if command == 'init':
        project = Project(empty=True)
        project.create()
        exit(0)
    if command == 'version':
        print version.__version__
        exit(0)

    Project.instance = Project()

    if command == 'sublime':
        create_sublime_project.run()
    elif command == 'inapps':
        inapps.run(Project.instance.package,
                   Project.instance.name,
                   Project.instance.version,
                   Project.instance.gg_inapps)
    elif command == 'build':
        build.run(Project.instance.package,
                  Project.instance.version,
                  parser)
    elif command == 'upload':
        build.upload(parser)
    elif command == 'upload_inapps':
        build.upload_inapps(parser)
    elif command == 'validate':
        validate.run()
    elif command == 'compress':
        compress_images.run(parser)
    else:
        print 'Unknown command [{}]'.format(command)


if __name__ == '__main__':
    sys.argv.extend('build -r /work/td_core/projects/syndicate-2 -p ios -c release'.split(' '))
    main()
