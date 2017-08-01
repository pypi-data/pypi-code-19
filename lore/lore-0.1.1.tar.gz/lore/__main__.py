#!/usr/bin/env python
import argparse
import sys

import lore


class HelpfulParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help(sys.stderr)
        self.exit(2, ('%s: error: %s\n') % (self.prog, message))

    
def main(args=None):
    parser = HelpfulParser(prog='lore')
    parser.add_argument('--version', action='version',
                        version='lore %s' % lore.__version__)

    commands = parser.add_subparsers( help='common commands')
    
    init_parser = commands.add_parser('init', help='create a new lore project')
    init_parser.set_defaults(func=init)
    init_parser.add_argument('NAME', help='the name of the project')
    init_parser.add_argument('--git-ignore', default=True)
    init_parser.add_argument('--python-version', default=None)

    install_parser = commands.add_parser(
        'install',
        help='install dependencies in a virtualenv'
    )
    install_parser.set_defaults(func=install)
    install_parser.add_argument(
        '--native',
        help='build optimized native dependencies (tensorflow)',
        action='store_true'
    )

    console_parser = commands.add_parser(
        'console',
        help='launch an interactive python shell'
    )
    console_parser.set_defaults(func=console)

    test_parser = commands.add_parser(
        'test',
        help='run tests'
    )
    test_parser.set_defaults(func=test)

    pip_parser = commands.add_parser(
        'pip',
        help='pass a command to this project\'s virtual env pip'
    )
    pip_parser.set_defaults(func=pip)

    python_parser = commands.add_parser(
        'python',
        help='pass a command to this project\'s virtual env python'
    )
    python_parser.set_defaults(func=python)

    (known, unknown) = parser.parse_known_args(args)
    known.func(known, unknown)
    

def init(parsed, unknown):
    lore.app.init()


def install(parsed, unknown):
    lore.app.install(parsed)


def console(parsed, unknown):
    lore.app.console()

    
def test(parsed, unknown):
    lore.app.test()


def pip(parsed, unknown):
    lore.app.pip_exec(unknown)


def python(parsed, unknown):
    lore.app.python_exec(unknown)
    
    
if __name__ == '__main__':
    main()
