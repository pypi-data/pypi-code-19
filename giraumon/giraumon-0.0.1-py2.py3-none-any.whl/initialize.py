# -*- coding: utf-8 -*-
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl).

from __future__ import print_function
import click
import sys
import os
from git import Repo
from git.exc import InvalidGitRepositoryError
from .utility import create_folder, create_manifest


@click.command()
@click.argument('path')
@click.option('-f', '--force', is_flag=True)
def init(path, force):
    """
    Initialize the structure for file in the git repository

    :param path: The path must be exists, if not it failed
    :type path: str
    :return: exit value from the system, 0 when successfull
    :rtype: int
    """
    if path == '.':
        path = os.getcwd()
    path = os.path.expanduser(path)

    click.echo('Initialise Hosting Configuration in "%s"' % path)

    # Check if repo contain is a git folder
    try:
        repo = Repo(path)
        print(repo)
    except InvalidGitRepositoryError:
        click.echo('%s Not a valid repository' % path)
        if not force:
            sys.exit(1)
        click.echo('Initialize "%s" as Git repository' % path)
        repo = Repo.init(path, bare=False)

    # check if path .platform exists
    pfdir = os.path.join(path, '.platform')
    create_folder(pfdir)
    create_manifest(pfdir)

    # Add templates folder
    tpdir = os.path.join(pfdir, 'templates')
    create_folder(tpdir, gitkeep=True)

    return sys.exit(0)
