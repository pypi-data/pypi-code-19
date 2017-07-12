#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Applicable to webstarts"""
import shlex
import subprocess

import click
from pkg_resources import get_distribution
from semantic_version import Version

__author__ = "john"


@click.group()
def cli():
  """CLI utilities"""


@cli.command('rel')
@click.option('-n', '--num')
def release(num):
  """Release prod

  Notes:
    setup.py develop
      Look into instead of pi -e .
    setup.py develop --uninstall
      Nice way to remove after when installing webstarts into sclime for example.
  """
  cmd(f'pip install .')
  version = num or _bump()
  cmd(f'git hf release start {version}')
  cmd(f'git hf release finish -M {version}')
  print(f'Dev: {_version()}')
  cmd('git checkout master')
  print(f'Master: {_version()}')
  cmd('python setup.py bdist_egg --skip-build')
  print(f'Deploy: {_version()}')
  cmd('./deploy.sh')


@cli.command()
def version():
  return print(f'Version: {_version()}')


@cli.command()
def bump():
  return print(f'Next Version: {_bump()}')


def _bump():
  v = Version.coerce(_version())
  if v.minor >= 9:
    return v.next_major()
  return v.next_minor()


def _version():
  return get_distribution('webstarts').version


def cmd(line, **kwargs):
  print(line)
  return subprocess.run(shlex.split(line), check=True, stdout=subprocess.PIPE, encoding='utf-8', **kwargs)
