#!/usr/bin/env python
# encoding: utf-8

"""
Feeding latex templates and compiling it
"""

import logging
import math as m
import subprocess
import random as rd
from path import Path
from .texenv import *

logger = logging.getLogger(__name__)

EXPORT_DICT = {}
EXPORT_DICT.update(m.__dict__)
EXPORT_DICT.update(rd.__dict__)
EXPORT_DICT.update(__builtins__)


def update_export_dict(new_dict):
    """Update global variable with new_dict

    It allows to import new functions (or modules) inside templates.

    :param new_dict: needed tools across all template renders
    """
    EXPORT_DICT.update(new_dict)


def feed(template, data, output="", force=0):
    """ Feed template with data to output

    :param template: jinja2 template with texenv environment
    :param data: Data dictionnary
    :param output: name of the output file
    (by default: tpl is replaced by a 2 digits number)
    :param force: Override is the output already exists
    """
    logger.info(f"Getting template {template}")
    tpl = texenv.get_template(str(template))

    if not output:
        num = 1
        output_p = Path(template.replace('tpl', f'{num:02d}'))
        while output_p.exists() and not force:
            logger.debug(f"{output_p} exists. Try next one")
            num += 1
            output_p = Path(template.replace('tpl', f'{num:02d}'))
    else:
        output_p = Path(output)
        if not force and output_p.exists():
            logger.error(f"{output} exists. Use force=1 do override it")
            raise ValueError(f"{output} exists. Use force=1 do override it")

    output_dir = output_p.dirname()
    if output_dir and not output_dir.exists():
        output_dir.mkdir_p()

    with open(output_p, "w") as output_f:
        output_f.write(tpl.render(**EXPORT_DICT, **data))
    logger.info(f"{template} has been rendered to {output}.")


def pdflatex(latex_file, output_dir=""):
    """ Compile latex file

    If output_dir is not set, it produce it next to the latex file.
    """
    if not output_dir:
        output_dir = Path(latex_file).dirname().abspath()
    logger.debug(f"output_dir for dflatex is {output_dir}")

    pwd = Path('./').abspath()
    Path(output_dir).cd()
    compilation = subprocess.Popen(
        [
            "pdflatex",
            # f"-output-directory={output_dir}",
            # "-halt-on-error",
            "-interaction=nonstopmode",
            "-shell-escape",
            str(Path(latex_file).name),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        # shell=True
        )

    for line in compilation.stdout:
        if b"Error" in line:
            logger.error(line)
    logger.debug(f"{latex_file.name} has been compiled in {output_dir}")
    pwd.cd()


def clean(dirname=".", garbages=["*.aux", "*.log"]):
    """ Clean the directory from aux and log latex files """
    if not dirname:
        dirname = Path("./")
    for g in garbages:
        g_files = Path(dirname).files(g)
        logger.debug(f"Remove {g_files}")
        for g_file in g_files:
            g_file.remove()

# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
