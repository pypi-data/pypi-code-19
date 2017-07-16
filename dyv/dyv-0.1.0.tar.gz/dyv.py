#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os
import re
from os.path import expanduser
import ConfigParser
import click
import sys
from pkg_resources import resource_filename, Requirement

import jinja2
from prettytable import PrettyTable

__VERSION__ = '0.1.0'
__AUTHOR__ = ''
__WEBSITE__ = ''
__DATE__ = ''

MANIFEST_FILE = '__manifest__.py'
OPENERP_FILE = '__openerp__.py'
INIT_FILE = '__init__.py'
ADDON_README_FILE = 'README.rst'
PROJECT_README_FILE = 'README.md'

ADDON_README_TEMPLATE_FILE = 'addon_readme.rst'
PROJECT_README_TEMPLATE_FILE = 'project_readme.md'

MODELS, VIEWS, WIZARD, CONTROLLERS, SECURITY, DATA = 'models', 'views', 'wizard', 'controllers', 'security', 'data'
SECURITY_FILE = 'ir.model.access.csv'
CONTROLLER_MAIN_FILE = 'main.py'

home = expanduser("~")
USERS_FILE = os.path.join(home, 'dyv_users.ini')
ADDONS_FILE = os.path.join(home, 'dyv_addons.ini')
PROJECTS_FILE = os.path.join(home, 'dyv_projects.ini')


def render(tpl_path, context):
    resource_path = os.path.sep.join(['dyv', tpl_path])
    tpl_path = resource_filename(__name__, resource_path)
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path)
    ).get_template(filename).render(context)


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__VERSION__)
    ctx.exit()


if not os.path.exists(USERS_FILE):
    with codecs.open(USERS_FILE, mode='w+', encoding='uft-8') as config_file:
        pass

if not os.path.exists(ADDONS_FILE):
    with codecs.open(ADDONS_FILE, mode='w+', encoding='uft-8') as config_file:
        pass

if not os.path.exists(PROJECTS_FILE):
    with codecs.open(ADDONS_FILE, mode='w+', encoding='uft-8') as config_file:
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
    user_keys = ['name', 'email', 'company', 'website']
    addon_keys = ['slug', 'name', 'version', 'summary', 'category', 'description', 'depends', 'icon']
    project_keys = ['name', 'slug', 'description', 'year', 'path']
    config_user_obj = ConfigParser.ConfigParser()
    config_addon_obj = ConfigParser.ConfigParser()
    config_project_obj = ConfigParser.ConfigParser()
    ctx.obj['config_user_obj'] = config_user_obj
    ctx.obj['config_addon_obj'] = config_addon_obj
    ctx.obj['config_project_obj'] = config_project_obj
    config_user_obj.read(USERS_FILE)
    config_addon_obj.read(ADDONS_FILE)
    config_project_obj.read(PROJECTS_FILE)
    if user:
        if user not in config_user_obj.sections():
            click.secho('The user %s not found' % user, fg='red')
            sys.exit(-1)
        else:
            for k in user_keys:
                ctx.obj['user_%s' % k] = config_user_obj.get(user, k, '')
    if addon:
        if addon not in config_addon_obj.sections():
            click.secho('The addon %s not found' % addon, fg='red')
            sys.exit(-1)
        else:
            for k in addon_keys:
                ctx.obj['addon_%s' % k] = config_addon_obj.get(addon, k, '')
    if project:
        if project not in config_project_obj.sections():
            click.secho('The project %s not found' % project, fg='red')
            sys.exit(-1)
        else:
            for k in project_keys:
                ctx.obj['project_%s' % k] = config_project_obj.get(project, k, '')
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
    ctx.obj['items'] = ['user', 'addon', 'project']

    def check(*elements):
        return all([ctx.obj.get(__i, False) for __i in elements])

    ctx.obj['check'] = check


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
    click.echo('Create new %s %s to the config %s' % (key, item_value, config_path))
    config.read(config_path)
    if item_value not in config.sections():
        config.add_section(item_value)
    else:
        click.secho('The %s %s already exists' % (key, item_value), fg='red')
        return
    for k in keys:
        default = ctx.obj.get('%s_%s' % (key, k), '')
        tmp = click.prompt(k, default=default, type=str)
        config.set(item_value, k, tmp)
    make_this_default(config, item_value)
    with codecs.open(config_path, mode='wb', encoding='utf-8') as configfile:
        config.write(configfile)
    click.secho('The %s %s is created' % (key, item_value), fg='green')


def __update_item(ctx, item_name, item_value):
    key, config_path = __get_items(item_name)
    config = ctx.obj['config_%s_obj' % key]
    keys = ctx.obj['%s_keys' % key]
    click.echo('Update %s %s from the config %s' % (key, item_value, config_path))
    config.read(config_path)
    if item_value not in config.sections():
        click.secho('The %s %s not found.' % (key, item_value), fg='red')
        return
    for k in keys:
        default = config.get(item_value, k, '')
        tmp = click.prompt(k, default=default, type=str)
        config.set(item_value, k, tmp)
    make_this_default(config, item_value)
    with codecs.open(config_path, mode='wb', encoding='utf-8') as configfile:
        config.write(configfile)
    click.secho('The %s %s is updated' % (key, item_value), fg='green')


def __use_section(ctx, item_name, item_value):
    if not item_value:
        item_value = find_or_create_section_for(ctx, item_name)
    key, config_path = __get_items(item_name)
    config = ctx.obj['config_%s_obj' % key]
    click.echo('Update %s %s from the config %s' % (key, item_value, config_path))
    config.read(config_path)
    if item_value not in config.sections():
        click.secho('The %s %s not found.' % (key, item_value), fg='red')
        return
    make_this_default(config, item_value)
    with codecs.open(config_path, mode='wb', encoding='utf-8') as configfile:
        config.write(configfile)
    click.secho('The %s %s will be used as default' % (key, item_value), fg='green')


def __delete_section(ctx, item_name, item_values):
    key, config_path = __get_items(item_name)
    config = ctx.obj['config_%s_obj' % key]
    click.echo('Delete %s %s from the config %s' % (key, item_values, config_path))
    config.read(config_path)
    for item_value in item_values:
        if item_value not in config.sections():
            click.secho('The %s %s not found.' % (key, item_value), fg='red')
        else:
            config.remove_section(item_value)
            click.secho('The %s %s is removed' % (key, item_value), fg='green')
    with codecs.open(config_path, mode='wb', encoding='utf-8') as configfile:
        config.write(configfile)


def __list_section(ctx, item_name):
    key, config_path = __get_items(item_name)
    config = ctx.obj['config_%s_obj' % key]
    keys = ctx.obj['%s_keys' % key]
    click.echo('List %ss from the config %s' % (key, config_path))
    config.read(config_path)
    x = PrettyTable()
    x.field_names = [item_name.title()] + [k.title() for k in keys] + ['Default']
    for f in x.field_names:
        x.align[f] = 'l'
    for section in config.sections():
        data = [config.get(section, k, '') for k in keys]
        x.add_row([section] + data + [config.get(section, 'default', '')])
    click.echo(x)


def __get_all_keys(ctx, additional_keys={}):
    all_keys = {}
    for item in ctx.obj['items']:
        section = ctx.obj[item]
        if section:
            key, config_path = __get_items(item)
            config = ctx.obj['config_%s_obj' % key]
            keys = ctx.obj['%s_keys' % key]
            config.read(config_path)
            if section not in config.sections():
                click.secho('The %s %s not found.' % (item, section), fg='red')
                continue
            for k in keys:
                all_keys['%s_%s' % (item, k)] = config.get(section, k, '')
    all_keys.update(additional_keys)
    all_keys['addon_name_len'] = len(all_keys.get('addon_name', ''))
    all_keys['project_name_len'] = len(all_keys.get('project_name', ''))
    all_keys['addon_depends'] = [x.strip().lower() for x in
                                 all_keys.get('addon_depends', '').replace(',', ':').replace(';', ':').replace(' ',
                                                                                                               ':').split(
                                     ':') if x]
    return all_keys


def __fix_keys(ctx):
    for item in ctx.obj['items']:
        key, config_path = __get_items(item)
        config = ctx.obj['config_%s_obj' % key]
        keys = ctx.obj['%s_keys' % key]
        for section in config.sections():
            for _k in keys:
                if not config.has_option(section, _k):
                    config.set(section, _k, '')

        with codecs.open(config_path, mode='wb', encoding='utf-8') as configfile:
            config.write(configfile)


def find_or_create_section_for(ctx, item_name):
    current_path = os.getcwd()
    key, config_path = __get_items(item_name)
    config = ctx.obj['config_%s_obj' % key]
    keys = ctx.obj['%s_keys' % key]
    config.read(config_path)
    for section in config.sections():
        if current_path == config.get(section, 'path', ''):
            make_this_default(config, section)
            return section
    section = click.prompt('Give a name for the section of the project')
    config.add_section(section)
    for k in keys:
        config.set(section, k, '')
    config.set(section, 'path', current_path)
    make_this_default(config, section)
    with codecs.open(config_path, mode='wb', encoding='utf-8') as configfile:
        config.write(configfile)
    return section


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
@click.argument('project', type=click.STRING, required=False)
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


@cli.command()
@click.pass_context
def keys(ctx):
    """Show the keys"""
    all_keys = __get_all_keys(ctx)
    x = PrettyTable()
    x.field_names = ['Key', 'Value']
    for f in x.field_names:
        x.align[f] = 'l'
    keys = sorted(all_keys.keys())
    for k in keys:
        x.add_row([k, all_keys.get(k)])
    click.echo(x)


@cli.command()
@click.pass_context
def fix_keys(ctx):
    """Fix the keys"""
    __fix_keys(ctx)
    click.secho('Keys are fixed', fg='green')


# ***************   GENERATING DATA   ***************#
def check_url_and_is_dir(url):
    if not url:
        return False, 'Please provide an URL' % url
    if not os.path.exists(url):
        return False, 'Url %s not found' % url
    if not os.path.isdir(url):
        return False, 'Url %s is not a directory' % url
    return True, os.path.abspath(url)


def check_url_and_is_file(url):
    if not url:
        return False, 'Please provide an URL' % url
    if not os.path.isfile(url):
        return False, 'Url %s is not a file' % url
    return True, os.path.abspath(url)


def check_url_and_is_addon(url):
    if not url:
        return False, 'Please provide an URL' % url
    if not os.path.isdir(url):
        return False, 'Url %s is not a directory' % url
    path_manifest = os.path.sep.join([url, MANIFEST_FILE])
    path_openerp = os.path.sep.join([url, OPENERP_FILE])
    if os.path.isfile(path_manifest):
        return True, path_manifest
    if os.path.isfile(path_openerp):
        return True, path_openerp
    return False, 'The directory %s is not an addon' % url


def go_and_patch_addon(project_path, addon_slug, all_keys, depends=None, **kwargs):
    click.echo('Creating the addon %s ...' % addon_slug)
    click.echo('args : %s' % kwargs)
    addon_path = os.path.join(project_path, addon_slug)
    if depends:
        depends = __clean_depends(depends)
        all_keys['addon_depends'] = depends
    if not os.path.exists(addon_path):
        os.mkdir(addon_path)
    manifest_path = os.path.join(addon_path, MANIFEST_FILE)
    root_init_path = os.path.join(addon_path, INIT_FILE)
    readme_path = os.path.join(addon_path, ADDON_README_FILE)
    if not os.path.isfile(manifest_path):
        with codecs.open(manifest_path, encoding='utf-8', mode='w+') as manifest_file:
            manifest_file.write(render(MANIFEST_FILE, all_keys))
    if not os.path.isfile(readme_path):
        with codecs.open(readme_path, mode='w+', encoding='utf-8') as addon_readme_file:
            addon_readme_file.write(render(ADDON_README_TEMPLATE_FILE, all_keys))
    if not os.path.isfile(root_init_path):
        with codecs.open(root_init_path, mode='w+', encoding='utf-8') as manifest_file:
            manifest_file.write('')

    if kwargs.get('controllers', []):
        controllers = kwargs.get('controllers', [])
        if controllers:
            create_dir([addon_path, CONTROLLERS])
            create_file([addon_path, INIT_FILE], add_content='from . import %s' % CONTROLLERS)
            create_file([addon_path, CONTROLLERS, INIT_FILE], add_content='from . import main')
            create_file([addon_path, CONTROLLERS, CONTROLLER_MAIN_FILE], add_content='# -*- coding: utf-8 -*-')
            create_file([addon_path, CONTROLLERS, CONTROLLER_MAIN_FILE], add_content='import http, registry')
            create_file([addon_path, CONTROLLERS, CONTROLLER_MAIN_FILE], add_content='from odoo.http import request')
        if hasattr(controllers, '__iter__'):
            for model_class in controllers:
                tmp = ''
                for x in model_class:
                    tmp += x if x.isalnum() else '.'
                model_class = tmp
                model_class = ''.join([x.title() for x in model_class.replace('_', '.').split('.') if x])
                create_file([addon_path, CONTROLLERS, CONTROLLER_MAIN_FILE],
                            add_content='class %s(http.Controller):' % model_class)
                create_file([addon_path, CONTROLLERS, CONTROLLER_MAIN_FILE],
                            add_content='    @http.route(\'/%s/index\', type=\'http\', auth="none")' % model_class.lower())
                create_file([addon_path, CONTROLLERS, CONTROLLER_MAIN_FILE],
                            add_content='    def %s_index(self, **kw):' % model_class.lower())
                create_file([addon_path, CONTROLLERS, CONTROLLER_MAIN_FILE],
                            add_content='        pass  # %s' % model_class)
    if kwargs.get('models', []):
        models = kwargs.get('models')
        if models:
            create_dir([addon_path, MODELS])
            create_file([addon_path, INIT_FILE], add_content='from . import %s' % MODELS)
        if hasattr(models, '__iter__'):
            for model in models:
                model = model.replace('.', '_')
                model_py = '%s.py' % model
                create_file([addon_path, MODELS, model_py], add_content='# -*- coding: utf-8 -*-')
                create_file([addon_path, MODELS, model_py], add_content='from odoo import models, fields, api, _')
                create_file([addon_path, MODELS, INIT_FILE], add_content='from . import %s' % model)
    if kwargs.get('views', []):
        views = kwargs.get('views', [])
        if views:
            create_dir([addon_path, VIEWS])
        if hasattr(views, '__iter__'):
            for model in views:
                model = model.replace('.', '_')
                model_xml = '%s.xml' % model
                create_file([addon_path, VIEWS, model_xml], add_content='<?xml version="1.0" encoding="UTF-8"?>')
                create_file([addon_path, VIEWS, model_xml], add_content='<odoo>')
                create_file([addon_path, VIEWS, model_xml], add_content='    <data>')
                create_file([addon_path, VIEWS, model_xml], add_content='    </data>')
                create_file([addon_path, VIEWS, model_xml], add_content='</odoo>')
                add_to_manifest([addon_path, MANIFEST_FILE], [VIEWS, model_xml])
    if kwargs.get('wizard', []):
        wizard = kwargs.get('wizard', [])
        if wizard:
            create_dir([addon_path, WIZARD])
            create_file([addon_path, INIT_FILE], add_content='from . import %s' % WIZARD)
        if hasattr(wizard, '__iter__'):
            for model in wizard:
                model = model.replace('.', '_')
                model_xml = '%s.xml' % model
                create_file([addon_path, WIZARD, model_xml], add_content='<?xml version="1.0" encoding="UTF-8"?>')
                create_file([addon_path, WIZARD, model_xml], add_content='<odoo>')
                create_file([addon_path, WIZARD, model_xml], add_content='    <data>')
                create_file([addon_path, WIZARD, model_xml], add_content='    </data>')
                create_file([addon_path, WIZARD, model_xml], add_content='</odoo>')
                add_to_manifest([addon_path, MANIFEST_FILE], [WIZARD, model_xml])
                model_py = '%s.py' % model
                create_file([addon_path, WIZARD, model_py], add_content='# -*- coding: utf-8 -*-')
                create_file([addon_path, WIZARD, model_py], add_content='from odoo import models, fields, api, _')
                create_file([addon_path, WIZARD, INIT_FILE], add_content='from . import %s' % model)

    if kwargs.get('data', []):
        data = kwargs.get('data', [])
        if data:
            create_dir([addon_path, DATA])
        if hasattr(data, '__iter__'):
            for model in data:
                model = model.replace('.', '_')
                model_xml = '%s.xml' % model
                create_file([addon_path, DATA, model_xml], add_content='<?xml version="1.0" encoding="UTF-8"?>')
                create_file([addon_path, DATA, model_xml], add_content='<odoo>')
                create_file([addon_path, DATA, model_xml], add_content='    <data>')
                create_file([addon_path, DATA, model_xml], add_content='    </data>')
                create_file([addon_path, DATA, model_xml], add_content='</odoo>')
                add_to_manifest([addon_path, MANIFEST_FILE], [DATA, model_xml])
    if kwargs.get('security', []):
        security = kwargs.get('security', [])
        if security:
            create_dir([addon_path, SECURITY])
            create_file([addon_path, SECURITY, SECURITY_FILE],
                        add_content='id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink')
            add_to_manifest([addon_path, MANIFEST_FILE], [SECURITY, SECURITY_FILE])
        if hasattr(security, '__iter__'):
            for model in security:
                model_underscore = model.replace('.', '_')
                create_file([addon_path, SECURITY, SECURITY_FILE],
                            add_content='access_%s_user,%s.user,model_%s,,1,0,0,0' % (
                                model_underscore, model, model_underscore))
                create_file([addon_path, SECURITY, SECURITY_FILE],
                            add_content='access_%s_manager,%s.manager,model_%s,,1,1,1,1' % (
                                model_underscore, model, model_underscore))

    click.secho("Addon <%s> patched in the project <%s>" % (addon_slug, project_path), fg='green')


def __clean_depends(deps):
    if hasattr(deps, '__iter__'):
        return list(deps)
    if isinstance(deps, basestring):
        deps = deps.strip().replace(' ', ':').replace(';', ';').replace(',', ':')
        deps = [x.strip().lower() for x in deps.split(':') if x.strip()]
    return deps


def create_dir(paths):
    path = os.path.sep.join(paths)
    if not os.path.exists(path):
        os.mkdir(path)


def add_to_manifest(manifest_paths, file_paths):
    manifest_file = os.path.sep.join(manifest_paths)
    file_path = '/'.join(file_paths)
    _insert_manifest_item(manifest_file, 'data', file_path)


def _insert_manifest_item(manifest_file, key, item):
    """ Insert an item in the list of an existing manifest key """
    with codecs.open(manifest_file, ) as f:
        manifest = f.read()
    if item in eval(manifest).get(key, []):
        return
    pattern = """(["']{}["']:\\s*\\[)""".format(key)
    repl = """\\1\n        '{}',""".format(item)
    manifest = re.sub(pattern, repl, manifest, re.MULTILINE)
    with codecs.open(manifest_file, mode='w+', encoding='utf-8') as f:
        f.write(manifest.decode(encoding='utf-8'))


def create_file(paths, contents=None, add_content=None):
    assert hasattr(paths, '__iter__'), 'paths should be a list or tuple'
    py_file = os.path.sep.join(paths)
    if not os.path.isfile(py_file):
        with codecs.open(py_file, mode='w+', encoding='utf-8') as pyfile:
            pyfile.write('')
    if contents:
        if contents not in open(py_file, 'r').read():
            with codecs.open(py_file, mode='w+', encoding='utf-8') as pyfile:
                pyfile.write(contents)
    content_lines = [x.rstrip() for x in open(py_file, 'r').readlines() if x]
    if add_content:
        if add_content not in content_lines:
            with codecs.open(py_file, mode='a+', encoding='utf-8') as pyfile:
                if len(content_lines) > 0 and content_lines[-1].strip():
                    add_content = '\n' + add_content
                pyfile.write(add_content)


@cli.command()
@click.argument('module_name', type=click.STRING, required=False)
@click.pass_context
def addon_patch(ctx, module_name):
    """Create or update an addon"""
    all_keys = __get_all_keys(ctx)
    if not ctx.obj['check']('user', 'project'):
        click.secho('please provide a user and a project', fg='red')
        return
    if not module_name and not ctx.obj['check']('addon'):
        click.secho('please provide an addon', fg='red')
        return
    pass_p, msg_p = check_url_and_is_dir(all_keys.get('project_path', ''))
    if not pass_p:
        click.secho('Project : %s' % msg_p, fg='red')
        return
    if module_name:
        all_keys['addon_slug'] = module_name
        pass_a, msg_a = check_url_and_is_addon(os.path.sep.join([all_keys.get('project_path', ''), module_name]))
        if not pass_a:
            click.secho('Addon : %s' % msg_a, fg='red')
            return
    if not all_keys.get('addon_slug', False):
        click.secho('please provide a name of the addon', fg='red')
        return
    addon_slug = module_name or all_keys.get('addon_slug')
    project_path = all_keys.get('project_path')
    if click.confirm('Continue to patch the addon %s in the project %s' % (addon_slug, project_path)):
        fuzzy = click.prompt('Enter the fuzzy string  model1:models:views model2:wizard')
        fuzzy = fuzzy.strip().lower()
        to_replace = ' ,:;-/@#&+'
        for tr in to_replace:
            fuzzy = fuzzy.replace(tr, '=')
        fuzzy = [x.strip() for x in fuzzy.split('=') if x]
        models = []
        groups = {}
        item_found = False
        for item in fuzzy:
            if item in ['models', 'views', 'wizard', 'data', 'controllers', 'security']:
                if item not in groups:
                    groups[item] = models[:]
                else:
                    groups[item] += models[:]
                item_found = True
            else:
                if item_found:
                    models = []
                    item_found = False
                models.append(item)
        go_and_patch_addon(all_keys.get('project_path'), all_keys.get('addon_slug'), all_keys, **groups)
    else:
        click.secho('Exit', fg='red')


@cli.command()
@click.pass_context
def project_patch(ctx):
    """Init or patch a project"""
    all_keys = __get_all_keys(ctx)
    if not ctx.obj['check']('user', 'project'):
        click.secho('please provide a user and a project', fg='red')
        return
    pass_p, msg_p = check_url_and_is_dir(all_keys.get('project_path', ''))
    if not pass_p:
        click.secho('Project : %s' % msg_p, fg='red')
        return
    if not all_keys.get('project_slug', False):
        click.secho('please provide a slug for the project', fg='red')
        return
    project_slug = all_keys.get('project_slug', '')
    project_name = all_keys.get('project_name', '')
    addons = {
        '%s_base' % project_slug: {
            'addon_depends': 'base',
            'addon_slug': '%s_base' % project_slug,
            'addon_name': '%s - Base' % project_name,
            'addon_category': 'Tools',
            'addon_summary': 'Module de base pour %s' % project_name,
            'addon_description': u"""
L'objectif de ce module est :
* Déclarer toutes les dépendances avec les modules standard et communautaires d'Odoo
* Ce module doit être déclaré dans les nouveaux modules créés
* Pour les nouveaux modules, il ne devrait pas dépendre des modules standard mais de ce module
* Pour mettre à jour les modules du projet, il suffit de mettre à jour ce module""",
        },
        '%s_recette' % project_slug: {
            'addon_depends': '%s_base' % project_slug,
            'addon_slug': '%s_recette' % project_slug,
            'addon_name': '%s - Recette' % project_name,
            'addon_category': 'Tools',
            'addon_summary': 'Module de recette pour %s' % project_name,
            'addon_description': u"""
L'objectif de ce module est de :
* Dépendre de tous les les modules spécifiques du projet
* Installer tous les modules lorsque ce module est installé
* Paraméter les données de la société""",
            'args': {
                'data': ['company'],
            }
        },
        '%s_demo' % project_slug: {
            'addon_depends': '%s_recette' % project_slug,
            'addon_slug': '%s_demo' % project_slug,
            'addon_name': u'%s - Démo' % project_name,
            'addon_category': 'Tools',
            'addon_summary': u'Module de démonstration pour %s' % project_name,
            'addon_description': u"""
L'objectif de ce module est de :
* Préparer des données pour la démonstration""",
            'args': {
                'data': True,
            }
        },
    }
    for addon, additional_keys in addons.iteritems():
        all_keys = __get_all_keys(ctx, additional_keys)
        go_and_patch_addon(all_keys.get('project_path'), all_keys.get('addon_slug'), all_keys,
                           **additional_keys.get('args', {}))
    readme_path = os.path.join(all_keys.get('project_path'), PROJECT_README_FILE)
    if not os.path.isfile(readme_path):
        with codecs.open(readme_path, encoding='utf-8', mode='w+') as readme_file:
            readme_file.write(render(PROJECT_README_TEMPLATE_FILE, all_keys))


if __name__ == '__main__':
    cli(obj={})


def main():
    return cli(obj={})
