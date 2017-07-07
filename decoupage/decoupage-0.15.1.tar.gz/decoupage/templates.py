#!/usr/bin/env python

"""
functionality related to templates
"""

import argparse
import os
import sys
from .index import index
from pkg_resources import iter_entry_points
from pkg_resources import resource_filename


def template_dirs():
    """
    returns set of registered template directories
    from `decoupage.formatters` setuptools entrypoint
    """

    template_dirs = set()
    for formatter in iter_entry_points('decoupage.formatters'):
        try:
            formatter.load()
        except:
            continue
        template_dir = resource_filename(formatter.module_name, 'templates')
        if os.path.isdir(template_dir):
            template_dirs.add(template_dir)
    return template_dirs


def templates():
    """return all registered templates"""

    templates = []
    for directory in template_dirs():
        templates.extend([os.path.join(directory, filename)
                          for filename in os.listdir(directory)
                          if filename.endswith('.html')])
    return templates


def template_dict():
    """return a dict of templates"""
    return {os.path.basename(template):template for template in templates()}


def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line
    description = """list and output available templates.
    If no argument is given list all full paths to templates.
    If `template` is provided, output its contents.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('template', nargs='?',
                        help="output this template")
    parser.add_argument('-o', '--output', dest='output',
                        help="output to file or directory or stdout")
    parser.add_argument('--cwd', dest='cwd',
                        action='store_true', default=False,
                        help="output to current working directory")
    options = parser.parse_args(args)

    # validate options
    if options.cwd:
        if options.output:
            parser.error("Overspecified: `--cwd` cannot be used with `--output`")
        options.output = os.getcwd()

    # retrieve templates
    _templates = template_dict()

    template = options.template
    if not template:
        # list templates and return
        for template in templates():
            print (template)
        return

    # look up template
    if not template.endswith('.html'):
        template += '.html'
    filename = _templates.get(template)
    if not filename:
        parser.error("Template '{}' not in {}".format(template, ', '.join(sorted(_templates.keys()))))
    content = open(filename, 'r').read()

    # divine output
    output = options.output
    if output:
        if os.path.isdir(output):
            output = os.path.join(output, 'index.html')
        with open(output, 'w') as f:
            f.write(content)
    else:
        print (content)


if __name__ == '__main__':
    main()
