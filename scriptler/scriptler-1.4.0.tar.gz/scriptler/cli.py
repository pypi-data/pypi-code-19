# -*- coding: utf-8 -*-
"""
.. module:: scriptler.cli
   :platform: Unix
   :synopsis: TODO.

.. moduleauthor:: Aljosha Friemann a.friemann@automate.wtf

----------------------------------------------------------------------------
"THE BEER-WARE LICENSE" (Revision 42):
<aljosha.friemann@gmail.com> wrote this file.  As long as you retain this
notice you can do whatever you want with this stuff. If we meet some day,
and you think this stuff is worth it, you can buy me a beer in return.
----------------------------------------------------------------------------

"""

import click, os, logging

from tabulate import tabulate
from simple_tools.lists import find
from simple_tools.conversions import bool2str

from scriptler.model import Config, Source, Script
from scriptler.config import parse_config, pretty_print, edit, save

from scriptler import scripts, __version__

logger = logging.getLogger(__name__)

def pretty_path(path):
    HOME = os.environ.get('HOME')
    return path.replace(HOME, '~')

pass_config = click.make_pass_decorator(Config)

default_paths = {
    'user': {
        'config': os.path.expanduser('~/.config/scriptler/config.yml'),
        'scripts': os.path.expanduser('~/.local/share/scriptler'),
    },
    'global': {
        'config': '/etc/scriptler/config.yml',
        'scripts': '/usr/local/share/scriptler',
    }
}

@click.group()
@click.option('--user/--global', default=True)
@click.option('-d', '--debug/--no-debug', default=False)
@click.option('-c', '--config', type=click.Path(dir_okay=False, exists=True))
@click.option('-s', '--script-dir', type=click.Path(file_okay=False))
@click.pass_context
def main(ctx, user, debug, config, script_dir):
    defaults = default_paths.get('user' if user else 'global')

    if config is None:
        config = defaults.get('config')

    if script_dir is None:
        script_dir = defaults.get('scripts')

    logging.basicConfig(level=logging.DEBUG if debug else logging.WARNING)
    ctx.obj = parse_config(
        config,
        defaults={'script_dir': script_dir, 'scripts': {}, 'sources': {}}
    )

@main.command()
def version():
    print('Scriptler %s' % __version__)

@main.command()
@pass_config
def remove(config):
    for script in scripts.get_all(config.script_dir):
        print('removing %s' % os.path.basename(script))
        scripts.remove(script)

@main.command()
@pass_config
def update(config):
    for script in config.scripts:
        print('installing %s' % script.name)

        source = None
        if script.source is not None:
            source = find(lambda s: s.name == script.source, config.sources)

        scripts.install(script.name, script, source, config.script_dir)

    for script in scripts.get_unmanaged(config.script_dir, config.scripts):
        print('removing unmanaged file %s' % os.path.basename(script))
        scripts.remove(script)

table_formats = [
    'plain',
    'simple',
    'grid',
    'fancy_grid',
    'pipe',
    'orgtbl',
    'rst',
    'mediawiki',
    'html',
    'latex',
    'latex_booktabs',
]

@main.command()
@click.option('-f', '--table-format', type=click.Choice(table_formats), default='simple')
@pass_config
def status(config, table_format):
    config_table = [
        ['config file', pretty_path(config.path)],
        ['script dir', pretty_path(config.script_dir)]
    ]

    print(tabulate(config_table, tablefmt='plain') + '\n')

    unmanaged_scripts = set( os.path.basename(s) for s in scripts.get_unmanaged(config.script_dir, config.scripts) )
    installed_scripts = set( os.path.basename(s) for s in scripts.get_all(config.script_dir) )

    script_table = [ (os.path.basename(s), bool2str(s not in unmanaged_scripts), bool2str(s in installed_scripts)) for s in installed_scripts ]

    print(tabulate(script_table, headers=['script', 'managed', 'installed'], tablefmt=table_format))

@main.group()
def config():
    pass

@config.command(name='view')
@pass_config
def config_view(config):
    pretty_print(config)

@config.command(name='edit')
@pass_config
def config_edit(config):
    return edit(config)

@main.group()
def add():
    pass

@add.command(name='source')
@pass_config
@click.option('-u', '--username')
@click.option('-p', '--password')
@click.option('-b', '--branch')
@click.argument('name')
@click.argument('url')
def add_source(config, username, password, branch, name, url):
    for source in config.sources:
        if source.name == name:
            raise AssertionError('Source with name {} already exists'.format(name))
        elif source.url == url:
            raise AssertionError('Source with url {} already exists ({})'.format(url, source.name))

    config.sources.append(Source(name=name, url=url, user=username, password=password, branch=branch))

    save(config)

@add.command(name='script')
@pass_config
@click.option('-c', '--command')
@click.argument('name')
@click.argument('source')
@click.argument('path')
def add_source(config, command, name, source, path):
    for script in config.scripts:
        if script.name == name:
            raise AssertionError('Source with name {} already exists'.format(name))
        elif script.source == source and script.path == path:
            raise AssertionError('Script from source {} and with path {} already exists ({})'.format(source, path, script.name))

    config.scripts.append(Script(name=name, path=path, source=source, command=command))

    save(config)

def run():
    try:
        return main()
    except AssertionError as e:
        raise RuntimeError(str(e))

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 fenc=utf-8
