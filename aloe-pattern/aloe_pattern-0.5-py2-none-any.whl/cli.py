import logging
import sass
import requests

from logging import critical, WARNING, DEBUG
from os import getcwd, sep
from os.path import dirname, abspath, join, isdir, commonprefix, split
from argparse import Action, ArgumentParser
from collections import OrderedDict

from partial import Rind, qualified, refresh
from files import fsref
from plotter import parser

class AloeError(RuntimeError):
    pass

def add_partials(args):
    """ Add partials to the plant """
    for target, rinddir in args.partials:
        if not target.exists:
            target.write()

        Rind(rinddir).link(target)

    refresh()

def remove_partials(args):
    """ Remove partials from the plant """
    for target, rinddir in args.partials:
        Rind(rinddir).unlink(target)

    refresh()

def fetch(args):
    dn, bn = split(abspath(args.partial))

    with open(qualified(dn, bn), 'w') as f:
        f.write(requests.get(args.url).text)


def build_rinds(args):
    """ Compile Sass found at rinds in user-specified order """
    for rindpath in args.rinds:
        print sass.compile(**{
            'filename': rindpath,
            'output_style': 'compressed' if args.prod else 'expanded',
        })

def plot(args):
    p = parser(args.production, **{
        'bemmy': args.bem_style,
        'shiftwidth': args.indent,
    })

    print p.parse()



class map_influence(Action):
    """
    `aloe + ...` translates to: [
        (<file user specified>, <build partial affected>),
        ...
    ]
    """
    def __call__(self, parser, namespace, values, option_string=None):
        wd = getcwd()
        out = []

        for pathspec in values:
            build_cursor = fsref(join(pathspec, Rind.filename))

            if commonprefix([wd, abspath(pathspec)]) != wd:
                raise AloeError('You cannot reference parent directories.')

            if isdir(pathspec) or build_cursor.exists:
                out.append((build_cursor, join(pathspec, '..')))
            else:
                dn, bn = split(pathspec)

                partial_cursor = fsref(qualified(dn, bn))
                out.append((partial_cursor, dn))

        setattr(namespace, self.dest, out)

class rinds_only(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        out = []
        for pathspec in values:
            if not pathspec.endswith(Rind.filename):
                pathspec = join(pathspec, Rind.filename)

            ref = fsref(pathspec)
            if not ref.exists:
                raise AloeError('No rind found at ' + pathspec)

            out.append(ref.abspath)

        setattr(namespace, self.dest, out)

def main():
    """ Start reading here. """
    parser = ArgumentParser(description="SCSS authoring CLI")

    parser.add_argument('-v', '--verbose', **{
        'action': 'store_true',
        'help': 'Print all actions to the console'
    })

    subparsers = parser.add_subparsers(help='Available commands')

    add = subparsers.add_parser('+', **{
        'help':'Link partials',
        'description':'Adds new partials to rinds.'
    })
    add.set_defaults(func=add_partials)
    add.add_argument('partials', **{
        'help': 'Partials to add',
        'nargs': '*',
        'action': map_influence,
    })

    rm = subparsers.add_parser('-', **{
        'help': 'Unlink partials',
        'description':'Removes partials from their rinds.'
    })
    rm.set_defaults(func=remove_partials)
    rm.add_argument('partials', **{
        'help': 'Partials to remove',
        'nargs': '*',
        'action': map_influence,
    })

    build = subparsers.add_parser('build', **{
        'help':'Build CSS from rinds',
        'description': 'Compiles CSS from the rinds created with Aloe',
    })
    build.set_defaults(func=build_rinds)
    build.add_argument('-p', '--prod', **{
        'action': 'store_true',
    })
    build.add_argument('rinds', **{
        'help': 'Rinds to build',
        'nargs': '*',
        'default': ['.'],
        'action': rinds_only,
    })

    fetchp = subparsers.add_parser('fetch', **{
        'help': 'Write text from URL to partial',
        'description': 'Fetches text resource from a URL and writes the'
                     + 'content to a given partial.'
    })
    fetchp.set_defaults(func=fetch)
    fetchp.add_argument('partial', **{
        'help': 'Name of partial'
    })
    fetchp.add_argument('url', **{
        'help': 'URL of text resource'
    })

    plotp = subparsers.add_parser('plot', **{
        'help':'Generate partial content from abbreviated stylesheet',
        'description': 'Writes a SCSS stylesheet to STDOUT using a single-line'
                     + ' abbreviation. Observe the difference between'
                     + ' `aloe plot "root", `aloe plot "root(leaf,leaf)"` and`'
                     + ' `aloe plot "root(leaf,branch(leaf,leaf))"` to'
                     + ' learn the pattern.'
    })
    plotp.set_defaults(func=plot)
    plotp.add_argument('production', **{
        'help': 'Stylesheet abbreviation',
    })
    plotp.add_argument('-i', '--indent', **{
        'help': 'Number of spaces used to indent SCSS',
        'type': int,
        'default': 4
    })
    plotp.add_argument('-b', '--bem-style', **{
        'help': 'Use &-refs in nested rulesets for BEM use cases.',
        'action': 'store_true',
        'default': False
    })


    try:
        logopts = {
            'format': '%(levelname)s: %(message)s',
        }

        logging.basicConfig(**logopts)

        args = parser.parse_args()

        root = logging.getLogger()
        root.setLevel(DEBUG if args.verbose else WARNING)

        return args.func(args)
    except AloeError as err:
        critical(err.message)
        return 1
