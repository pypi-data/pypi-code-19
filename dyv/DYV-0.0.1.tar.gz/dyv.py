#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from os.path import expanduser
import ConfigParser
import click
from prettytable import PrettyTable

__VERSION__ = '0.0.1'
__AUTHOR__ = ''
__WEBSITE__ = ''
__DATE__ = ''

home = expanduser("~")
USERS_FILE = os.path.join(home, 'dyv_users.ini')
ADDONS_FILE = os.path.join(home, 'dyv_addons.ini')
PROJECTS_FILE = os.path.join(home, 'dyv_projects.ini')


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__VERSION__)
    ctx.exit()


if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w+') as config_file:
        pass

if not os.path.exists(ADDONS_FILE):
    with open(ADDONS_FILE, 'w+') as config_file:
        pass

if not os.path.exists(PROJECTS_FILE):
    with open(ADDONS_FILE, 'w+') as config_file:
        pass


@click.group()
@click.option('--user', '-u', type=click.STRING, help="The user to load")
@click.option('--addon', '-a', type=click.STRING, help="The addon to load")
@click.option('--project', '-p', type=click.STRING, help="The project to load")
@click.option('--version', '-v', is_flag=True, callback=print_version, expose_value=False, is_eager=True,
              help="Show the version")
@click.pass_context
def cli(ctx, user, addon, project):
    """CLI for DYV"""
    user_keys = ['name', 'company', 'website']
    addon_keys = ['name', 'summary', 'category', 'description', 'icon', 'path']
    project_keys = ['name', 'slug', 'year', 'path']
    config_user_obj = ConfigParser.ConfigParser()
    config_addon_obj = ConfigParser.ConfigParser()
    config_project_obj = ConfigParser.ConfigParser()
    ctx.obj['config_user_obj'] = config_user_obj
    ctx.obj['config_addon_obj'] = config_addon_obj
    ctx.obj['config_project_obj'] = config_project_obj
    config_user_obj.read(USERS_FILE)
    config_addon_obj.read(ADDONS_FILE)
    config_project_obj.read(PROJECTS_FILE)
    if not user:
        for _sec in config_user_obj.sections():
            default = config_user_obj.has_option(_sec, 'default') and config_user_obj.getboolean(_sec,
                                                                                                 'default') or False
            if default:
                user = _sec
    if not addon:
        for _sec in config_addon_obj.sections():
            default = config_addon_obj.has_option(_sec, 'default') and config_addon_obj.getboolean(_sec,
                                                                                                   'default') or False
            if default:
                addon = _sec
    if not project:
        for _sec in config_project_obj.sections():
            default = config_project_obj.has_option(_sec, 'default') and config_project_obj.getboolean(_sec,
                                                                                                       'default') or False
            if default:
                project = _sec
    if user:
        if user not in config_user_obj.sections():
            click.secho('The user %s not found' % user, fg='red')
        else:
            for k in user_keys:
                ctx.obj[k] = config_user_obj.get(user, k, '')
    if addon:
        if addon not in config_addon_obj.sections():
            click.secho('The addon %s not found' % addon, fg='red')
        else:
            for k in addon_keys:
                ctx.obj[k] = config_addon_obj.get(addon, k, '')
    if project:
        if project not in config_project_obj.sections():
            click.secho('The project %s not found' % project, fg='red')
        else:
            for k in project_keys:
                ctx.obj[k] = config_project_obj.get(project, k, '')
    ctx.obj['user'] = user
    ctx.obj['addon'] = addon
    ctx.obj['project'] = project
    ctx.obj['user_keys'] = user_keys
    ctx.obj['addon_keys'] = addon_keys
    ctx.obj['project_keys'] = project_keys
    if user:
        click.secho('Use the user %s as default' % user, fg='green')
    if addon:
        click.secho('Use the addon %s as default' % addon, fg='green')
    if project:
        click.secho('Use the project %s as default' % project, fg='green')


def make_this_default(__config, __section):
    for tmp_section in __config.sections():
        if tmp_section == __section:
            __config.set(tmp_section, 'default', True)
        else:
            __config.set(tmp_section, 'default', False)


def __get_items(key):
    if key == 'user':
        return 'user', USERS_FILE
    elif key == 'addon':
        return 'addon', ADDONS_FILE
    elif key == 'project':
        return 'project', PROJECTS_FILE


def __create_item(ctx, item_name, item_value):
    key, config_path = __get_items(item_name)
    config = ctx.obj['config_%s_obj' % key]
    keys = ctx.obj['%s_keys' % key]
    click.echo('Create new %s %s to the config %s' % (key, item_value, USERS_FILE))
    config.read(config_path)
    if item_value not in config.sections():
        config.add_section(item_value)
    else:
        click.secho('The %s %s already exists' % (key, item_value), fg='red')
        return
    for k in keys:
        default = ctx.obj[k] if ctx.obj['%s' % key] else ''
        tmp = click.prompt(k, default=default, type=str)
        config.set(item_value, k, tmp)
    make_this_default(config, item_value)
    with open(config_path, 'wb') as configfile:
        config.write(configfile)
    click.secho('The %s %s is created' % (key, item_value), fg='green')


def __update_item(ctx, item_name, item_value):
    key, config_path = __get_items(item_name)
    config = ctx.obj['config_%s_obj' % key]
    keys = ctx.obj['%s_keys' % key]
    click.echo('Update %s %s from the config %s' % (key, item_value, USERS_FILE))
    config.read(config_path)
    if item_value not in config.sections():
        click.secho('The %s %s not found.' % (key, item_value), fg='red')
        return
    for k in keys:
        default = config.get(item_value, k, '')
        tmp = click.prompt(k, default=default, type=str)
        config.set(item_value, k, tmp)
    make_this_default(config, item_value)
    with open(config_path, 'wb') as configfile:
        config.write(configfile)
    click.secho('The %s %s is updated' % (key, item_value), fg='green')


def __use_section(ctx, item_name, item_value):
    key, config_path = __get_items(item_name)
    config = ctx.obj['config_%s_obj' % key]
    click.echo('Update %s %s from the config %s' % (key, item_value, USERS_FILE))
    config.read(config_path)
    if item_value not in config.sections():
        click.secho('The %s %s not found.' % (key, item_value), fg='red')
        return
    make_this_default(config, item_value)
    with open(config_path, 'wb') as configfile:
        config.write(configfile)
    click.secho('The %s %s will be used as default' % (key, item_value), fg='green')


def __delete_section(ctx, item_name, item_values):
    key, config_path = __get_items(item_name)
    config = ctx.obj['config_%s_obj' % key]
    click.echo('Delete %s %s from the config %s' % (key, item_values, USERS_FILE))
    config.read(config_path)
    for item_value in item_values:
        if item_value not in config.sections():
            click.secho('The %s %s not found.' % (key, item_value), fg='red')
        else:
            config.remove_section(item_value)
            click.secho('The %s %s is removed' % (key, item_value), fg='green')
    with open(config_path, 'wb') as configfile:
        config.write(configfile)


def __list_section(ctx, item_name):
    key, config_path = __get_items(item_name)
    config = ctx.obj['config_%s_obj' % key]
    keys = ctx.obj['%s_keys' % key]
    click.echo('List %ss from the config %s' % (key, USERS_FILE))
    config.read(config_path)
    x = PrettyTable()
    x.field_names = [item_name.title()] + [k.title() for k in keys] + ['Default']
    for f in x.field_names:
        x.align[f] = 'l'
    for section in config.sections():
        data = [config.get(section, k, '') for k in keys]
        x.add_row([section] + data + [config.get(section, 'default', '')])
    click.echo(x)


@cli.command()
@click.argument('user', type=click.STRING, required=True)
@click.pass_context
def user_create(ctx, user):
    """Create a new user"""
    __create_item(ctx, 'user', user)


@cli.command()
@click.argument('addon', type=click.STRING, required=True)
@click.pass_context
def addon_create(ctx, addon):
    """Create a new addon"""
    __create_item(ctx, 'addon', addon)


@cli.command()
@click.argument('project', type=click.STRING, required=True)
@click.pass_context
def project_create(ctx, project):
    """Create a new project"""
    __create_item(ctx, 'project', project)


@cli.command()
@click.argument('user', type=click.STRING, required=True)
@click.pass_context
def user_update(ctx, user):
    """Update a user"""
    __update_item(ctx, 'user', user)


@cli.command()
@click.argument('addon', type=click.STRING, required=True)
@click.pass_context
def addon_update(ctx, addon):
    """Update an addon"""
    __update_item(ctx, 'addon', addon)


@cli.command()
@click.argument('project', type=click.STRING, required=True)
@click.pass_context
def project_update(ctx, project):
    """Update a project"""
    __update_item(ctx, 'project', project)


@cli.command()
@click.argument('user', type=click.STRING, required=True)
@click.pass_context
def user_use(ctx, user):
    """Use a user a default"""
    __use_section(ctx, 'user', user)


@cli.command()
@click.argument('project', type=click.STRING, required=True)
@click.pass_context
def project_use(ctx, project):
    """Use a project as default"""
    __use_section(ctx, 'project', project)


@cli.command()
@click.argument('addon', type=click.STRING, required=True)
@click.pass_context
def addon_use(ctx, addon):
    """Use an addon as default"""
    __use_section(ctx, 'addon', addon)


@cli.command()
@click.argument('user', type=click.STRING, required=True, nargs=-1)
@click.pass_context
def user_delete(ctx, user):
    """Delete a user"""
    __delete_section(ctx, 'user', user)


@cli.command()
@click.argument('addon', type=click.STRING, required=True, nargs=-1)
@click.pass_context
def addon_delete(ctx, addon):
    """Delete an addon"""
    __delete_section(ctx, 'addon', addon)


@cli.command()
@click.argument('project', type=click.STRING, required=True, nargs=-1)
@click.pass_context
def project_delete(ctx, project):
    """Delete an project"""
    __delete_section(ctx, 'project', project)


@cli.command()
@click.pass_context
def users(ctx):
    """Show users"""
    __list_section(ctx, 'user')


@cli.command()
@click.pass_context
def addons(ctx):
    """Show users"""
    __list_section(ctx, 'addon')


@cli.command()
@click.pass_context
def projects(ctx):
    """Show projects"""
    __list_section(ctx, 'project')


@cli.command()
@click.pass_context
def table(ctx):
    """Show the table"""
    __list_section(ctx, 'project')
    __list_section(ctx, 'user')
    __list_section(ctx, 'addon')


# ***************   GENERATING DATA   ***************#

@cli.command()
@click.pass_context
def addon_generate(ctx):
    """Generate data"""


if __name__ == '__main__':
    cli(obj={})


def main():
    return cli(obj={})
