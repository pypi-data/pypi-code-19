#!/usr/bin/env python2.7
# coding=utf-8
"""A tool that provides syncing capabilities between folders on the same or an external host."""

import click
from scandir import walk
from sh import rsync, ssh
from pathlib2 import Path
import os
import errno

# http://click.pocoo.org/5/commands/
# https://pathlib.readthedocs.io/en/pep428/
# Coloring output http://click.pocoo.org/5/utils/

ssh_connection_uri = None
DEFAULT_ROOT_SYNC_PATH = "/media/cada/transfer/sync"

excludes = {'/media/Windows/Users/genzo/Dropbox/transfer', '.cache', 'VirtualBox VMs',
            'Downloads', '.vagrant.d', '.dropbox', 'venv', 'Videos', '*.pyc', "compile-cache",
            '*.tmp', '*.*~', 'nohup.out', 'system/caches'}


def _silent_delete(path):
    try:
        os.remove(path.as_posix())
    except OSError as error:
        if error.errno == errno.ENOENT:  # errno.ENOENT = no such file or directory
            pass
        else:
            raise


def _synchronize_mappings(sync_mappings):
    for from_path, to_path in sync_mappings:

        if ssh_connection_uri:
            ssh(ssh_connection_uri, 'mkdir', '-p', to_path.as_posix())
            to_uri = ssh_connection_uri + ':' + to_path.as_posix()
        else:
            to_path.mkdir(parents=True, exist_ok=True)
            to_uri = to_path.as_posix()

        exclude_params = zip(len(excludes) * ['--exclude'], excludes)

        rsync('-rltv', from_path.as_posix() + '/', to_uri + '/', delete=True, *exclude_params)


def _print_sync_mappings(sync_mappings):
    for from_path, to_path in sync_mappings:
        if to_path.exists():
            status = click.style('exists', fg="green", bold=True)
        else:
            status = click.style("doesn't exist", fg="red", bold=True)

        click.echo('{:>60} -> {:<60} {:>8}'.format(from_path, to_path, '(' + status + ')'))


def _get_sync_paths(from_path, excludes, to_path):
    for root, directories, files in walk(from_path):
        if '.exclude' in files and to_path not in root:
            excludes |= {root}

        if '.sync' in files:
            if not any(x in root for x in excludes):
                yield Path(root)


@click.group()
@click.option('--root_sync_path', '-r', type=click.Path(exists=True),
              default=DEFAULT_ROOT_SYNC_PATH)
@click.pass_context
def sync(ctx, root_sync_path):
    ctx.obj['root_sync_path'] = root_sync_path


@sync.command()
@click.pass_context
def store(ctx):
    """Sync directories in the home dir that contains a .sync file to the *root_sync_path*."""
    root_sync_path = ctx.obj['root_sync_path']

    sync_paths = _get_sync_paths('/home/cada', excludes | {root_sync_path}, root_sync_path)
    synchronization_mappings = [(path, Path(root_sync_path) / path.relative_to('/'))
                                for path in sync_paths]
    _print_sync_mappings(synchronization_mappings)
    _synchronize_mappings(synchronization_mappings)


@sync.command()
@click.pass_context
def load(ctx):
    """Sync directories in *root_sync_path* that contains a .sync file to the home dir."""
    root_sync_path = ctx.obj['root_sync_path']
    sync_paths = _get_sync_paths(root_sync_path, excludes, root_sync_path)

    if not sync_paths:
        raise click.UsageError(
            message="No paths configured for sync could be found in {}".format(root_sync_path),
            ctx=ctx)

    synchronization_mappings = [(path, Path('/') / path.relative_to(root_sync_path))
                                for path in sync_paths]
    _print_sync_mappings(synchronization_mappings)
    _synchronize_mappings(synchronization_mappings)


@sync.command()
@click.pass_context
def list(ctx):
    """List the relation between directories in your home directory and the *root_sync_path*."""
    root_sync_path = ctx.obj['root_sync_path']

    click.echo('\nSyncs from {} to {}'.format('/home/cada', root_sync_path))
    sync_paths = _get_sync_paths('/home/cada', excludes | {root_sync_path}, root_sync_path)
    sync_mappings = [(path, Path(root_sync_path) / path.relative_to('/'))
                     for path in sync_paths]
    _print_sync_mappings(sync_mappings)

    click.echo('\nSyncs from {} to {}'.format(root_sync_path, '/home/cada'))
    sync_paths = _get_sync_paths(root_sync_path, excludes, root_sync_path)
    sync_mappings = [(path, Path('/') / path.relative_to(root_sync_path))
                     for path in sync_paths]
    _print_sync_mappings(sync_mappings)


@sync.command()
@click.pass_context
@click.argument('path', type=click.Path(exists=True))
def unlink(ctx, path):
    """Unlink a path from the home folder and delete the backup folder"""

    root_sync_path = ctx.obj['root_sync_path']
    sync_file_path = Path(path) / '.sync'

    try:
        os.remove(sync_file_path.as_posix())
    except OSError as error:
        if error.errno == errno.ENOENT:
            raise click.UsageError('{} is not synchronized'.format(path))
        else:
            raise
    else:
        backup_folder_path = root_sync_path / sync_file_path.parent.relative_to('/')
        _silent_delete(backup_folder_path)


def main():
    sync(obj={})


if __name__ == '__main__':
    main()
