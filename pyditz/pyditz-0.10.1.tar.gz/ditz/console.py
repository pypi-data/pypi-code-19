"""
Main console program.
"""

from __future__ import print_function

import os
import sys
import argparse

from .config import config, config_path
from .logger import init_logging
from .version import __version__

# Name of the main program.
progname = "pyditz"


def main(args=sys.argv[1:]):
    # Build command parser.
    parser = argparse.ArgumentParser(prog=progname)

    parser.add_argument("--version", action="version",
                        version="%(prog)s version " + __version__)

    parser.add_argument("-v", "--verbose", action="store_true",
                        help="be verbose about things")

    parser.add_argument("--traceback", action="store_true",
                        help="print traceback on error")

    group = parser.add_argument_group("global arguments")

    group.add_argument("-i", "--issue-dir", type=str, metavar="DIR",
                       help="use the given issue directory")

    group = parser.add_argument_group("configuration arguments")

    group.add_argument("-u", "--user-config", type=str, metavar="FILE",
                       help="use the given user config file")

    group.add_argument("-c", "--config", type=str, action="append",
                       metavar="SECTION.OPTION=VALUE",
                       help="set a config option explicitly")

    group = parser.add_argument_group("feature arguments")

    group.add_argument("-S", "--no-search", action="store_true",
                       help="turn off searching of parent directories")

    group.add_argument("-P", "--no-pager", action="store_true",
                       help="turn off paging of output")

    group.add_argument("-H", "--no-highlight", action="store_true",
                       help="turn off syntax highlighting")

    group.add_argument("-N", "--no-setup", action="store_true",
                       help="turn off interactive setup")

    group.add_argument("-X", "--no-plugins", action="store_true",
                       help="turn off loading of external plugins")

    group.add_argument("-V", "--no-vcs", action="store_true",
                       help="turn off use of version control")

    group = parser.add_argument_group("comment arguments")

    group.add_argument("-m", "--comment", type=str, metavar="STRING",
                       help="specify a comment in commands")

    group.add_argument("-n", "--no-comment", action="store_true",
                       help="skip asking for a comment in commands")

    group = parser.add_argument_group("information arguments")

    group.add_argument("-p", "--path", type=str,
                       choices=["repo", "issues", "project"],
                       help="print path information")

    # Prepend arguments from environment, if any.
    flags = os.environ.get("DITZFLAGS", None)
    if flags:
        args = flags.split() + args

    # Parse arguments.
    opts, args = parser.parse_known_args(args)

    try:
        # Initialise.
        init_logging(opts.verbose)

        if opts.user_config:
            config.set_file(opts.user_config)

        if opts.config:
            for setting in opts.config:
                config.set_option(setting)

        pathinfo = opts.path
        issuedir = opts.issue_dir or "."

        # Either show information or run commands.
        if not pathinfo:
            run_commands(opts, args, issuedir)
        else:
            show_path_info(pathinfo, issuedir)

    except KeyboardInterrupt:
        if opts.traceback:
            raise
        else:
            print()
            sys.exit("%s: aborted" % progname)

    except Exception as msg:
        if opts.traceback:
            raise
        else:
            sys.exit("%s: error: %s" % (progname, msg))


def run_commands(opts, args, issuedir):
    """
    Run a single command or enter command loop.
    """

    from .plugin import loader
    from .settings import Settings
    from .util import terminal_size

    # Build common settings to pass to Ditz command.
    settings = Settings(autosave=True, usecache=True)

    if opts.no_highlight:
        settings.highlight = False
    else:
        settings.highlight = config.getboolean('highlight', 'enable')

    if opts.no_vcs:
        settings.versioncontrol = False
    else:
        settings.versioncontrol = config.getboolean('vcs', 'enable')

    cols, lines = terminal_size()
    settings.termlines = 0 if opts.no_pager else lines
    settings.termcols = cols

    settings.externalplugins = not opts.no_plugins
    settings.searchparents = not opts.no_search
    settings.setup = not opts.no_setup

    settings.nocomment = opts.no_comment
    settings.comment = opts.comment

    # Set up plugin load paths.
    if settings.externalplugins:
        # Load plugins from user config directory.
        path = config_path("plugins")
        loader.add_path(path)

        # Load setuptools plugins.
        loader.add_entrypoint('ditz.plugin')

    # Load plugins.
    loader.load()

    # Run things.
    from .commands import DitzCmd

    if not args:
        cmd = DitzCmd(issuedir, settings=settings, interactive=True)
        cmd.cmdloop()
    else:
        cmd = DitzCmd(issuedir, settings=settings)
        command = " ".join(args)
        if not cmd.onecmd(command):
            sys.exit(99)


def show_path_info(pathtype, issuedir):
    """
    Show path information.
    """

    from .objects import Project, find_config
    from .util import DitzError

    repodir, conf = find_config(issuedir, error=True)

    if pathtype == 'repo':
        path = repodir
    elif pathtype == 'issues':
        path = os.path.join(repodir, conf.issue_dir)
    elif pathtype == 'project':
        path = os.path.join(repodir, conf.issue_dir, Project.filename)
    else:
        raise DitzError("invalid path option")

    print(path)


if __name__ == "__main__":
    main()
