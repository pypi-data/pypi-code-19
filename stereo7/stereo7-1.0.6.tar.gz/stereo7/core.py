import version
import argparse
import inapps
import os
import project
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
    project.instance = project.Project()

    if args.c == 'inapps':
        inapps.run(project.instance.package,
                   project.instance.name,
                   project.instance.version,
                   project.instance.gg_inapps)
    else:
        print 'Unknown command [{}]'.format(args.c)


if __name__ == '__main__':
    main()
