#!/usr/bin/env python
# encoding: utf-8

import logging
import jinja2

logger = logging.getLogger(__name__)

__all__ = [
        "texenv",
        "add_filter",
        "add_pkg_loader",
        "add_path_loader",
        ]

# Definition of jinja syntax for latex
texenv = jinja2.Environment(
    block_start_string='\Block{',
    block_end_string='}',
    variable_start_string='\Var{',
    variable_end_string='}',
    comment_start_string='\#{',
    comment_end_string='}',
    line_statement_prefix='%-',
    line_comment_prefix='%#',
    loader=jinja2.ChoiceLoader([
        # jinja2.PackageLoader("notes_tools.reports", "templates"),
        jinja2.FileSystemLoader(['./']),
        ]),
    extensions=['jinja2.ext.do']
)

def add_filter(filtername, filterfunc):
    """ Append the filter to texenv

    :param filtername: The filter name
    :param filterfunc: The fiter function
    """
    texenv.filters[filtername] = filterfunc


def add_pkg_loader(pkgname, tpl):
    """ Add a package where templates can be choosen """
    texenv.loader.loaders.append(jinja2.PackageLoader(
        pkgname,
        tpl
        ))


def add_path_loader(path):
    """ Add a path where templates can be choosen """
    texenv.loader.loaders.append(jinja2.FileSystemLoader(path))


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del 
