#!/usr/bin/env python
# -*- coding: utf-8 -*-

__VERSION__ = '0.3.5'
__AUTHOR__ = ''
__WEBSITE__ = ''
__DATE__ = ''

import odoorpc
from odoorpc.tools import v
import ConfigParser
import click
from prettytable import PrettyTable
import os
import sys
import time
import random as pkg_random
import base64 as pkg_base64
import uuid as pkg_uuid
import string as pkg_string
import xlsxwriter
import code
import signal
from pprint import pprint
from os.path import expanduser
from lxml import etree

home = expanduser("~")
CONFIG_FILE = os.path.join(home, 'dyz.ini')


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__VERSION__)
    ctx.exit()


if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'w+') as config_file:
        pass


def raise_keyboard_interrupt(*a):
    raise KeyboardInterrupt()


class Console(code.InteractiveConsole):
    def __init__(self, locals=None, filename="<console>"):
        code.InteractiveConsole.__init__(self, locals, filename)
        try:
            import readline
            import rlcompleter
        except ImportError:
            print 'readline or rlcompleter not available, autocomplete disabled.'
        else:
            readline.set_completer(rlcompleter.Completer(locals).complete)
            readline.parse_and_bind("tab: complete")


class Shell(object):
    def init(self, args):
        signal.signal(signal.SIGINT, raise_keyboard_interrupt)

    def console(self, local_vars):
        if not os.isatty(sys.stdin.fileno()):
            exec sys.stdin in local_vars
        else:
            Console(locals=local_vars).interact()


@click.group()
@click.option('--database', '-d', type=click.STRING, default='DEMO', help="The database")
@click.option('--host', '-h', type=click.STRING, default='localhost', help="The host of the server")
@click.option('--load', '-l', type=click.STRING, help="The name of section to load")
@click.option('--prompt-login', type=click.BOOL, is_flag=True, help="Prompt the Odoo parameters for loggin")
@click.option('--prompt-connect', type=click.BOOL, is_flag=True, help="Prompt the Odoo parameters for connection")
@click.option('--config', '-c',
              type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=True, readable=True,
                              resolve_path=True), default=CONFIG_FILE, help="The path of config")
@click.option('--export', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True, readable=True,
                                          resolve_path=True))
@click.option('--port', '-p', type=click.INT, default=8069, help="The port of the server")
@click.option('--user', '-u', type=click.STRING, default='admin', help="The user of the database")
@click.option('--password', '-pass', type=click.STRING, default='admin', help="The password of the user")
@click.option('--superuserpassword', '-s', type=click.STRING, default='admin', help="The password of the super user")
@click.option('--protocol', type=click.Choice(['jsonrpc+ssl', 'jsonrpc']), default='jsonrpc', help="Protocol to use")
@click.option('--mode', '-m', type=click.Choice(['test', 'dev', 'prod']), default='dev', help="Database mode")
@click.option('--timeout', '-t', type=click.INT, default=60, help="Timeout in minutes")
@click.option('--version', '-v', is_flag=True, callback=print_version, expose_value=False, is_eager=True,
              help="Show the version")
@click.pass_context
def cli(ctx, database, host, port, user, password, superuserpassword, protocol, timeout, config, load, mode, export,
        prompt_login, prompt_connect):
    """CLI for Odoo"""

    odoo = False
    prompt_connect = prompt_login or prompt_connect

    def export_excel(data_to_export):
        if export:
            filename = 'EXPORT_%s.xlsx' % time.strftime('%Y%m%d_%H%M%S')
            export_file = os.path.join(export, filename)
            workbook = xlsxwriter.Workbook(export_file)
            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': True})
            col, row = 0, 0
            for i, filename in enumerate(data_to_export._field_names):
                worksheet.write(row, col, str(data_to_export._field_names[i]), bold)
                col += 1
            for i, rowdata in enumerate(data_to_export._rows):
                row += 1
                col = 0
                for j, coldata in enumerate(data_to_export._rows[i]):
                    worksheet.write(row, col, str(coldata))
                    col += 1
            workbook.close()
            click.secho("The data is exported to %s" % export_file, fg='green')

    def echo(data_to_show):
        click.echo(data_to_show)
        export_excel(data_to_show)

    def secho(data_to_show, fg=None, bg=None):
        click.secho(data_to_show, fg=fg, bg=bg)
        export_excel(data_to_show)

    def xml_id(record, record_id=False):
        global odoo
        if not record:
            return ''
        if not record_id:
            res_model, res_id = record._name, record.id
        else:
            res_model, res_id = record, record_id
        IrModelData = odoo.env['ir.model.data']
        data_id = IrModelData.search([('model', '=', res_model), ('res_id', '=', res_id)])
        data = IrModelData.browse(data_id)
        return data.complete_name if data else ''

    def object_from_xml_id(xmlid):
        global odoo
        if not xmlid:
            return False
        xmlid_tuple = xmlid.strip().split('.')
        module = False
        if len(xmlid_tuple) == 2:
            module, xml_name = xmlid_tuple
        else:
            xml_name = xmlid
        IrModelData = odoo.env['ir.model.data']
        model_domain = [('name', '=', xml_name)]
        if module:
            model_domain.append(('module', '=', module))
        data_id = IrModelData.search(model_domain)
        data = IrModelData.browse(data_id)
        if data:
            return odoo.env[data.model].browse(data.res_id)
        return False

    def action_connect():
        global odoo
        if mode == 'prod':
            if not click.confirm('You are in mode production, continue ?'):
                sys.exit()
        try:
            click.secho('Try to connect to the host %s:%s, database=%s, mode=%s, timeout=%smin' % (
                host, port, database, mode, timeout / 60))
            odoo = odoorpc.ODOO(host, protocol=protocol, port=port, timeout=timeout)
            click.secho('Connected to host %s:%s, database=%s, version=%s, mode=%s, timeout=%smin' % (
                host, port, database, odoo.version, mode, timeout / 60),
                        fg='green')
            ctx.obj['version'] = int(
                ''.join([x for x in odoo.version.strip() if x.isdigit() or x == '.']).split('.')[0])
        except:
            click.secho(
                'Cannot connect to host %s:%s, database=%s, mode=%s' % (host, port, database, mode),
                fg='red')
        return odoo

    def action_login():
        global odoo
        odoo = action_connect()
        if odoo:
            odoo = odoorpc.ODOO(host, protocol=protocol, port=port, timeout=timeout)
            try:
                click.secho('Try to login to the database %s as %s' % (database, user))
                odoo.login(database, user, password)
                click.secho('Connected to the database %s as %s' % (database, user), fg="green")
            except:
                click.secho('Cannot connect to the database %s as %s' % (database, user), fg="red")
        return odoo

    def update_list():
        global odoo
        if odoo:
            click.echo('Updating the list of modules ...')
            odoo.env['ir.module.module'].update_list()

    timeout *= 30

    config_obj = ConfigParser.ConfigParser()
    ctx.obj['config_obj'] = config_obj
    ctx.obj['config_path'] = config
    ctx.obj['load'] = load
    config_obj.read(config)
    if not load:
        for _sec in config_obj.sections():
            default = config_obj.has_option(_sec, 'default') and config_obj.getboolean(_sec, 'default') or False
            if default:
                load = _sec
    load_from_config = load and load in config_obj.sections()
    if load_from_config:
        click.secho('Loading data from the config file ...')
    ctx.obj['_database'] = database
    ctx.obj['_host'] = host
    ctx.obj['_port'] = port
    ctx.obj['_user'] = user
    ctx.obj['_password'] = password
    ctx.obj['_protocol'] = protocol
    ctx.obj['_superuserpassword'] = superuserpassword
    ctx.obj['_mode'] = mode
    ctx.obj['_default'] = False

    database = config_obj.get(load, 'database', database) if load_from_config else database
    host = config_obj.get(load, 'host', host) if load_from_config else host
    port = config_obj.getint(load, 'port') if load_from_config else port
    user = config_obj.get(load, 'user', user) if load_from_config else user
    password = config_obj.get(load, 'password', password) if load_from_config else password
    protocol = config_obj.get(load, 'protocol', protocol) if load_from_config else protocol
    mode = config_obj.get(load, 'mode', mode) if load_from_config else mode
    superuserpassword = config_obj.get(load, 'superuserpassword',
                                       superuserpassword) if load_from_config else superuserpassword
    if prompt_connect:
        host = click.prompt('host', host, type=str)
        port = click.prompt('port', default=port, type=str)
        superuserpassword = click.prompt('superuserpassword', default=superuserpassword, type=str)
        protocol = click.prompt('protocol', protocol, type=str)
    ctx.obj['prompt_database'] = False
    if prompt_login:
        ctx.obj['prompt_database'] = True
        database = click.prompt('database', default=database, type=str)
        user = click.prompt('user', default=user, type=str)
        password = click.prompt('password', default=password, type=str)
        mode = click.prompt('mode', default=mode, type=str)
    ctx.obj['database'] = database
    ctx.obj['host'] = host
    ctx.obj['port'] = port
    ctx.obj['user'] = user
    ctx.obj['password'] = password
    ctx.obj['protocol'] = protocol
    ctx.obj['superuserpassword'] = superuserpassword
    ctx.obj['mode'] = mode
    ctx.obj['odoo'] = odoo
    ctx.obj['action_login'] = action_login
    ctx.obj['action_connect'] = action_connect
    ctx.obj['odoo'] = odoo
    ctx.obj['xml_id'] = xml_id
    ctx.obj['object_from_xml_id'] = object_from_xml_id
    ctx.obj['echo'] = echo
    ctx.obj['secho'] = secho
    ctx.obj['update_list'] = update_list


@cli.command()
@click.argument('section', type=click.STRING, required=True)
@click.option('--fields', '-f', type=click.STRING, required=False, multiple=True)
@click.pass_context
def section_save(ctx, section, fields):
    """Save the config"""
    config = ctx.obj['config_obj']
    config_path = ctx.obj['config_path']
    click.echo('Save the config %s to %s' % (section, config_path))
    config.read(config_path)
    if section not in config.sections():
        config.add_section(section)
    config.set(section, 'database', 'database' in fields and ctx.obj['_database'] or ctx.obj['database'])
    config.set(section, 'host', 'host' in fields and ctx.obj['_host'] or ctx.obj['host'])
    config.set(section, 'port', 'port' in fields and ctx.obj['_port'] or ctx.obj['port'])
    config.set(section, 'user', 'user' in fields and ctx.obj['_user'] or ctx.obj['user'])
    config.set(section, 'password', 'password' in fields and ctx.obj['_password'] or ctx.obj['password'])
    config.set(section, 'default', 'default' in fields and ctx.obj['_default'] or ctx.obj['default'])
    config.set(section, 'superuserpassword',
               'superuserpassword' in fields and ctx.obj['_superuserpassword'] or ctx.obj['superuserpassword'])
    config.set(section, 'protocol', 'protocol' in fields and ctx.obj['_protocol'] or ctx.obj['protocol'])
    config.set(section, 'mode', 'mode' in fields and ctx.obj['_mode'] or ctx.obj['mode'])
    with open(ctx.obj['config_path'], 'wb') as configfile:
        config.write(configfile)


@cli.command()
@click.argument('section', type=click.STRING, required=True)
@click.pass_context
def section_create(ctx, section):
    """Create a new section"""
    config = ctx.obj['config_obj']
    config_path = ctx.obj['config_path']
    click.echo('Create new section %s to the config %s' % (section, config_path))
    config.read(config_path)
    if section not in config.sections():
        config.add_section(section)
    else:
        click.secho('The section %s already exists' % section, fg='red')
        return
    host = click.prompt('host', default=ctx.obj['host'], type=str)
    port = click.prompt('port', default=ctx.obj['port'], type=str)
    database = click.prompt('database', default=ctx.obj['database'], type=str)
    user = click.prompt('user', default=ctx.obj['user'], type=str)
    password = click.prompt('password', default=ctx.obj['password'], type=str)
    superuserpassword = click.prompt('superuserpassword', default=ctx.obj['superuserpassword'], type=str)
    protocol = click.prompt('protocol', default=ctx.obj['protocol'], type=str)
    mode = click.prompt('mode', default=ctx.obj['mode'], type=str)
    config.set(section, 'host', host)
    config.set(section, 'port', port)
    config.set(section, 'database', database)
    config.set(section, 'user', user)
    config.set(section, 'password', password)
    config.set(section, 'superuserpassword', superuserpassword)
    config.set(section, 'protocol', protocol)
    config.set(section, 'mode', mode)
    with open(ctx.obj['config_path'], 'wb') as configfile:
        config.write(configfile)
    click.secho('The section %s is created' % section, fg='green')


@cli.command()
@click.argument('section', type=click.STRING, required=True)
@click.pass_context
def section_update(ctx, section):
    """Update a section"""
    config = ctx.obj['config_obj']
    config_path = ctx.obj['config_path']
    click.echo('Update the section %s in the config %s' % (section, config_path))
    config.read(config_path)
    if section not in config.sections():
        click.secho('The section %s does not found' % section, fg='red')
        return
    host = click.prompt('host', default=config.get(section, 'host'), type=str)
    port = click.prompt('port', default=config.get(section, 'port'), type=str)
    database = click.prompt('database', default=config.get(section, 'database'), type=str)
    user = click.prompt('user', default=config.get(section, 'user'), type=str)
    password = click.prompt('password', default=config.get(section, 'password'), type=str)
    superuserpassword = click.prompt('superuserpassword', default=config.get(section, 'superuserpassword'), type=str)
    protocol = click.prompt('protocol', default=config.get(section, 'protocol'), type=str)
    mode = click.prompt('mode', default=config.get(section, 'mode'), type=str)
    config.set(section, 'host', host)
    config.set(section, 'port', port)
    config.set(section, 'database', database)
    config.set(section, 'user', user)
    config.set(section, 'password', password)
    config.set(section, 'superuserpassword', superuserpassword)
    config.set(section, 'protocol', protocol)
    config.set(section, 'mode', mode)
    with open(ctx.obj['config_path'], 'wb') as configfile:
        config.write(configfile)
    click.secho('The section %s is updated' % section, fg='green')


@cli.command()
@click.argument('section', type=click.STRING, required=True)
@click.pass_context
def section_use(ctx, section):
    """Use a section"""
    __use_section(ctx, section)


@cli.command()
@click.argument('section', type=click.STRING, required=True)
@click.pass_context
def section_set(ctx, section):
    """Set a section"""
    __use_section(ctx, section)


def __use_section(ctx, section):
    """Set a section"""
    config = ctx.obj['config_obj']
    config_path = ctx.obj['config_path']
    click.echo('Set the section %s in the config %s' % (section, config_path))
    config.read(config_path)
    if section not in config.sections():
        click.secho('The section %s does not found' % section, fg='red')
        return
    for _sec in config.sections():
        config.set(_sec, 'default', False)
    config.set(section, 'default', True)
    with open(ctx.obj['config_path'], 'wb') as configfile:
        config.write(configfile)
    click.secho('The section %s is default' % section, fg='green')


@cli.command()
@click.pass_context
def section_unset(ctx):
    """Unset a section"""
    config = ctx.obj['config_obj']
    config_path = ctx.obj['config_path']
    click.echo('Unset the default section in the file %s' % config_path)
    config.read(config_path)
    for section in config.sections():
        config.set(section, 'default', False)
    with open(ctx.obj['config_path'], 'wb') as configfile:
        config.write(configfile)
    click.secho('The default section is unset', fg='green')


@cli.command()
@click.argument('section', type=click.STRING, required=True, nargs=-1)
@click.pass_context
def section_delete(ctx, section):
    """Delete a section"""
    config = ctx.obj['config_obj']
    config_path = ctx.obj['config_path']
    click.echo('Delete sections %s from the config %s' % (section, config_path))
    config.read(config_path)
    for sec in section:
        if sec not in config.sections():
            click.secho('The section %s does not found' % sec, fg='red')
            continue
        else:
            config.remove_section(sec)
            click.secho('The section %s is removed' % sec, fg='green')
    with open(ctx.obj['config_path'], 'wb') as configfile:
        config.write(configfile)


@cli.command()
@click.pass_context
@click.argument('arg', type=click.STRING, required=False)
def section_list(ctx, arg):
    """Show section list"""
    __section_list(ctx, arg)


@cli.command()
@click.pass_context
@click.argument('arg', type=click.STRING, required=False)
def sections(ctx, arg):
    __section_list(ctx, arg)


def __section_list(ctx, arg):
    """Show section list"""
    config = ctx.obj['config_obj']
    echo = ctx.obj['echo']
    config_path = ctx.obj['config_path']
    click.echo('List sections of the config')
    config.read(config_path)
    x = PrettyTable()
    if not arg:
        x.field_names = ["Section", "Database", "Host", "Port", "User", "Password", "Super User Password", "Protocol",
                         "Mode", "Default"]
    else:
        x.field_names = ["Section", "Database", arg.title()]
    for f in x.field_names:
        x.align[f] = 'l'
    for section in config.sections():
        if not arg:
            x.add_row([
                section,
                config.get(section, 'database', ''),
                config.get(section, 'host', ''),
                config.get(section, 'port', ''),
                config.get(section, 'user', ''),
                config.get(section, 'password', ''),
                config.get(section, 'superuserpassword', ''),
                config.get(section, 'protocol', ''),
                config.get(section, 'mode', ''),
                config.get(section, 'default', ''),
            ])
        else:
            x.add_row([
                section,
                config.get(section, 'database', ''),
                config.get(section, arg, ''),
            ])
    echo(x)


# Misc

@cli.command()
@click.argument('length', type=click.INT, default=24, required=False)
@click.option('--nbr', type=click.INT, default=1, required=False)
@click.option('--uuid', is_flag=True, type=click.BOOL, default=False, required=False)
@click.option('--base64', is_flag=True, type=click.BOOL, default=False, required=False)
@click.pass_context
def random(ctx, length, nbr, uuid, base64):
    """Generate random strings"""
    click.echo('Some random strings')
    echo = ctx.obj['echo']
    tab = []
    for i in range(nbr):
        if uuid:
            generated_string = str(pkg_uuid.uuid1())
        elif base64:
            generated_string = pkg_base64.b64encode(os.urandom(length))
        else:
            generated_string = ''.join(pkg_random.choice(pkg_string.letters + pkg_string.digits) for _ in range(length))
        tab.append(generated_string)
    x = PrettyTable()
    x.field_names = ["Random"]
    x.align["Random"] = "l"
    for r in tab:
        x.add_row([r])
    echo(x)


# Managing database

@cli.command()
@click.argument('output', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True, readable=True,
                                          resolve_path=True), required=True)
@click.pass_context
def db_backup(ctx, output):
    """Backup the database"""
    database = ctx.obj['database']
    filename = '%s_%s.zip' % (database, time.strftime('%Y%m%d_%H%M%S'))
    path = os.path.join(output, filename)
    click.echo('Backup the database %s to %s' % (database, path))
    dump = ctx.obj['action_connect']().db.dump(ctx.obj['superuserpassword'], database)
    f = open(path, 'wb+')
    f.write(dump.getvalue())
    f.close()
    click.secho('The backup is stored to %s' % path, fg='green')


@cli.command()
@click.argument('input', type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True,
                                         resolve_path=True), required=True)
@click.pass_context
def db_restore(ctx, input):
    """Restore a database"""
    database = ctx.obj['database']
    click.echo('Restore the database %s from %s' % (database, input))
    with open(input, 'rb') as backup_file:
        ctx.obj['action_connect']().db.restore(ctx.obj['superuserpassword'], database, backup_file)
    click.echo('The database is restored')


@cli.command()
@click.pass_context
def db_drop(ctx):
    """Drop the database"""
    database = ctx.obj['database']
    click.echo('Drop the database %s ' % database)
    if click.confirm('Do you want to continue?'):
        ctx.obj['action_connect']().db.drop(ctx.obj['superuserpassword'], database)
        click.secho('The database is dropped', fg='green')
    else:
        click.secho('The database is not dropped', fg='red')


@cli.command()
@click.pass_context
def db_create(ctx):
    """Create a database"""
    ctx.obj['action_connect']()
    database = ctx.obj['database']
    if not ctx.obj['prompt_database']:
        database = click.prompt('Name of the database ?', database)
    click.echo('Create the database %s ' % database)
    demo = False
    lang = click.prompt('Language ?', 'fr_FR')
    if click.confirm('Load demo data ?'):
        demo = True
    if click.confirm('Do you want to continue?'):
        odoo.db.create(admin_password=ctx.obj['superuserpassword'], db=database, demo=demo, lang=lang,
                       password=ctx.obj['superuserpassword'])
        click.secho('The database is created', fg='green')
    else:
        click.secho('The database is not created', fg='red')


@cli.command()
@click.pass_context
def db_list(ctx):
    """List databases"""
    click.echo('List databases')
    odoo = ctx.obj['action_connect']()
    echo = ctx.obj['echo']
    x = PrettyTable()
    x.field_names = ["Name"]
    x.align["Name"] = "l"
    for db in odoo.db.list():
        x.add_row([db])
    echo(x)


# Access database

@cli.command()
@click.pass_context
def login(ctx):
    """Login to the database"""
    ctx.obj['action_login']()


@cli.command()
@click.pass_context
def shell(ctx):
    """Shell mode"""

    def model(model_name):
        return odoo.env[model_name]

    def browse_by_domain(model_name, domain=[], limit=0, order='id asc'):
        return odoo.env[model_name].browse(odoo.env[model_name].search(domain, limit=limit, order=order))

    def browse_by_ids(model_name, ids):
        return odoo.env[model_name].browse(ids)

    def read(model_name, domain=[], fields=[], limit=0):
        return odoo.env[model_name].search_read(domain, fields, limit=limit)

    def count(model_name, domain=[]):
        return odoo.env[model_name].search_count(domain)

    def show(records, field='name'):
        if not isinstance(records, (list, tuple)):
            for rec in records:
                print "%s : %s" % (str(rec.id).rjust(3, ' '), getattr(rec, field, ''))
        else:
            for rec in records:
                print "%s : %s" % (str(rec.get('id')).rjust(3, ' '), rec.get(field, ''))

    m = model
    bbd = browse_by_domain
    bpids = browse_by_ids
    browse = browse_by_domain
    pp = pprint
    odoo = ctx.obj['action_login']()
    Shell().console(locals())


@cli.command()
@click.pass_context
def connect(ctx):
    """Connect to the server"""
    ctx.obj['action_connect']()


@cli.command()
@click.argument('model', type=click.STRING, required=True)
@click.option('--filter', '-f', type=click.STRING, required=False, multiple=True)
@click.option('--states', '-ss', type=click.BOOL, is_flag=True, required=False, default=False)
@click.option('--store', '-s', type=click.BOOL, is_flag=True, required=False, default=False)
@click.option('--depends', '-d', type=click.BOOL, is_flag=True, required=False, default=False)
@click.option('--required', '-r', type=click.BOOL, is_flag=True, required=False, default=False)
@click.option('--readonly', '-ro', type=click.BOOL, is_flag=True, required=False, default=False)
@click.option('--domain', type=click.BOOL, is_flag=True, required=False, default=False)
@click.option('--translate', '-t', type=click.BOOL, is_flag=True, required=False, default=False)
@click.option('--relation', type=click.BOOL, is_flag=True, required=False, default=False)
@click.option('--selection', type=click.BOOL, is_flag=True, required=False, default=False)
@click.option('--help', type=click.BOOL, is_flag=True, required=False, default=False)
@click.pass_context
def fields(ctx, model, filter, store, states, depends, required, readonly, domain, translate, relation, selection,
           help):
    """List fields of a model"""
    click.echo('Showing the fields of the model %s' % model)
    odoo = ctx.obj['action_login']()
    echo = ctx.obj['echo']
    Model = odoo.env[model]
    x = PrettyTable()
    # x.field_names = ["Name", "Type", "Label", "Relation/Selection", "Store", "Depends", "Required", "States"]
    header = ["Name", "Type", "Label"]
    if store:
        header.append('Store')
    if states:
        header.append('States')
    if depends:
        header.append('Depends')
    if required:
        header.append('Required')
    if readonly:
        header.append('Readonly')
    if domain:
        header.append('Domain')
    if translate:
        header.append('Translate')
    if relation:
        header.append('Relation')
    if selection:
        header.append('Selection')
    if help:
        header.append('Help')
    x.field_names = header

    x.align["Name"] = x.align["Type"] = x.align["Label"] = "l"
    # x.align["Name"] = x.align["Type"] = x.align["Label"] = x.align["Relation/Selection"] = x.align["States"] = "l"
    # x.align["Store"] = x.align["Depends"] = x.align["Required"] = "c"
    for key, value in Model.fields_get().iteritems():
        show = False
        if not filter:
            show = True
        elif value.get('type') in filter or key in filter or value.get('relation', False) in filter:
            show = True
        else:
            for f in filter:
                if f in value.get('type') or f in key or f in value.get('relation', ''):
                    show = True
        if show:
            relation_selection = value.get('relation', '')
            if not relation_selection and value.get('selection', ''):
                relation_selection = ','.join([tmp[0] for tmp in value.get('selection', '')])
            tab = [key, value.get('type', ''), value.get('string', '')]
            from pprint import pprint
            pprint(value)
            if store:
                tab.append(value.get('store', ''))
            if states:
                tab.append(value.get('states', ''))
            if depends:
                tab.append(','.join([tmp for tmp in value.get('depends', '')]))
            if required:
                tab.append(value.get('required', ''))
            if readonly:
                tab.append(value.get('readonly', ''))
            if domain:
                tab.append(value.get('domain', ''))
            if translate:
                tab.append(value.get('translate', ''))
            if relation:
                tab.append(value.get('relation', ''))
            if selection:
                tab.append(','.join([tmp[0] for tmp in value.get('selection', '')]))
            if help:
                tab.append(value.get('help', ''))
            x.add_row(tab)
            # x.add_row([key, value.get('type', ''), value.get('string', ''), relation_selection, value.get('store', ''),
            #            value.get('depends', ''), value.get('required', ''), value.get('states', '')])
    echo(x)


@cli.command()
@click.argument('model', type=click.STRING, required=True)
@click.argument('function', type=click.STRING, required=True)
@click.option('--id', default=False, type=click.STRING, required=False, multiple=True)
@click.option('--param', '-p', default=False, nargs=2, type=click.STRING, required=False, multiple=True)
@click.pass_context
def func(ctx, model, function, id, param):
    """Execute a function"""
    click.echo('Execute the function %s of the model %s' % (function, model))
    odoo = ctx.obj['action_login']()
    Model = odoo.env[model]
    if id:
        ids = [int(x) for x in id]
        Model = Model.browse(ids)
    args = {}
    for p_key, p_value in param:
        try:
            p_value = eval(p_value)
        except:
            pass
        args[p_key] = p_value
    click.echo('ids=%s, args=%s' % (id, args))
    click.echo(getattr(Model, function)(**args))


@cli.command()
@click.pass_context
def module_update_list(ctx):
    """Update list of modules"""
    odoo = ctx.obj['action_login']()
    ctx.obj['update_list']()
    click.secho('The list of module is updated', fg='green')


@cli.command()
@click.argument('modules', type=click.STRING, required=True)
@click.option('--module', '-m', type=click.STRING, multiple=True)
@click.option('--update-list', is_flag=True, default=False, type=click.BOOL)
@click.pass_context
def module_install(ctx, modules, module, update_list):
    """Install modules"""
    odoo = ctx.obj['action_login']()
    if update_list:
        ctx.obj['update_list']()
    for module in [x.strip() for x in modules.split(',')] + list(module):
        click.echo('Installing the module : %s ' % module)
        Module = odoo.env['ir.module.module']
        module_id = Module.search([('name', '=', module)])
        if module_id:
            Module.button_immediate_install(module_id)
            click.secho('The module %s is installed' % module, fg='green')
        else:
            click.secho('The module %s is not installed' % module, fg='red')


@cli.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=False, readable=True,
                                        resolve_path=True), default=home)
@click.option('--update-list', is_flag=True, default=False, type=click.BOOL)
@click.pass_context
def module_install_all(ctx, path, update_list):
    """Install modules"""
    odoo = ctx.obj['action_login']()
    if update_list:
        ctx.obj['update_list']()
    modules = []
    for root, dirnames, filenames in os.walk(path):
        for dirname in dirnames:
            for _root, _dirnames, _filenames in os.walk(os.path.join(root, dirname)):
                for filename in _filenames:
                    if filename in ['__openerp__.py', '__manifest__.py']:
                        modules.append(dirname)

    for module in modules:
        click.echo('Installing the module : %s ' % module)
        Module = odoo.env['ir.module.module']
        module_id = Module.search([('name', '=', module)])
        if module_id:
            Module.button_immediate_install(module_id)
            click.secho('The module %s is installed' % module, fg='green')
        else:
            click.secho('The module %s is not installed' % module, fg='red')


@cli.command()
@click.argument('modules', type=click.STRING, required=True)
@click.option('--module', '-m', type=click.STRING, multiple=True)
@click.option('--update-list', is_flag=True, default=False, type=click.BOOL)
@click.pass_context
def module_update(ctx, modules, module, update_list):
    """Upgrade modules"""
    odoo = ctx.obj['action_login']()
    if update_list:
        ctx.obj['update_list']()
    for module in [x.strip() for x in modules.split(',')] + list(module):
        click.echo('Updating the module : %s ' % module)
        Module = odoo.env['ir.module.module']
        module_id = Module.search([('name', '=', module)])
        if module_id:
            Module.button_immediate_upgrade(module_id)
            click.secho('The module %s is upgraded' % module, fg='green')
        else:
            click.secho('The module %s is not upgraded' % module, fg='red')


@cli.command()
@click.argument('model', type=click.STRING, required=True)
@click.option('--domain', '-d', nargs=3, help='Filter the records', multiple=True)
@click.pass_context
def truncate(ctx, model, domain):
    """Truncate an object"""
    odoo = ctx.obj['action_login']()
    final_domain = []
    if domain:
        for d in domain:
            field, operator, value = d
            try:
                value = eval(value)
            except:
                pass
            final_domain.append((field, operator, value))
    Model = odoo.env[model]
    model_ids = Model.search(final_domain)
    if click.confirm('Are you sure you want to delete %s records from %s with the domain %s' % (
            len(model_ids), model, final_domain)):
        success, error = 0, 0
        for model_id in model_ids:
            try:
                Model.unlink(model_id)
                click.secho('the record #%s is deleted' % model_id, fg='green')
                success += 1
            except:
                click.secho('the record #%s can not deleted' % model_id, fg='red')
                error += 1
        click.echo('success: %s, error: %s' % (success, error))
        Model.unlink(model_ids)
    else:
        click.secho('The truncate is aborted !')


@cli.command()
@click.argument('modules', type=click.STRING, required=True)
@click.option('--module', '-m', type=click.STRING, multiple=True)
@click.option('--update-list', is_flag=True, default=False, type=click.BOOL)
@click.pass_context
def module_uninstall(ctx, modules, module, update_list):
    """Uninstall modules"""
    odoo = ctx.obj['action_login']()
    if update_list:
        ctx.obj['update_list']()
    for module in [x.strip() for x in modules.split(',')] + list(module):
        click.echo('Uninstalling the module : %s ' % module)
        Module = odoo.env['ir.module.module']
        module_id = Module.search([('name', '=', module)])
        if module_id:
            Module.button_uninstall(module_id)
            click.secho('The module %s is uninstalled' % module, fg='green')
        else:
            click.secho('The module %s is not uninstalled' % module, fg='red')


@cli.command()
@click.argument('model', type=click.STRING, required=True)
@click.argument('params', type=click.STRING, required=False)
@click.pass_context
def refs(ctx, model, params):
    """Searching the XML-IDS related to the model"""
    click.echo('Inspect the XML-IDS of the model %s ' % model)
    if '=' in model or '&' in model:
        params = model
    action_param = menu_param = view_type_param = record_id_param = False
    if params:
        for param_expression in params.split('&'):
            param_tuple = param_expression.split('=')
            if len(param_tuple) == 2:
                _k = param_tuple[0].split('#')[-1]
                _v = param_tuple[1].isdigit() and int(param_tuple[1]) or param_tuple[1]
                if _k == 'menu_id': menu_param = _v
                if _k == 'action': action_param = _v
                if _k == 'view_type': view_type_param = _v
                if _k == 'id': record_id_param = _v
                if _k == 'model': model = _v
    odoo = ctx.obj['action_login']()
    echo = ctx.obj['echo']
    xml_id = ctx.obj['xml_id']
    Action = odoo.env['ir.actions.act_window']
    Menu = odoo.env['ir.ui.menu']
    Values = odoo.env['ir.values']
    View = odoo.env['ir.ui.view']
    view_domain = [('model', '=', model)]
    if view_type_param:
        view_domain.append(('type', '=', view_type_param))
    view_ids = View.search(view_domain)
    blacklist = []
    action_domain = [('res_model', '=', model)]
    if action_param:
        action_domain.append(('id', '=', action_param))
    action_ids = Action.search(action_domain)
    if record_id_param:
        click.secho('')
        click.secho('Data XML-ID', fg='blue')
        x = PrettyTable()
        x.field_names = ["DATA XML-ID"]
        for f in x.field_names:
            x.align[f] = 'l'
        x.add_row([xml_id(odoo.env[model].browse(int(record_id_param)))])
        echo(x)


    x = PrettyTable()
    x_menu = PrettyTable()
    x.field_names = ["Action Name", "Action ID", "Action XML-ID", "Menu Name", "Menu ID", "Menu XML-ID"]
    x_menu.field_names = ["ID", "Menu Name", "Full Path"]
    for f in x.field_names:
        x.align[f] = 'l'
    for f in x_menu.field_names:
        x_menu.align[f] = 'l'
    for action in Action.browse(action_ids):
        if v(odoo.version) < v('9.0'):
            menu_domain = [('value', '=', 'ir.actions.act_window,%s' % action.id)]
            if menu_param:
                menu_domain.append(('res_id', '=', menu_param))
            values = Values.search_read(menu_domain, ['res_id'])
            menu_ids = [_x.get('res_id') for _x in values]
        else:
            menu_domain = [('action', '=', 'ir.actions.act_window,%s' % action.id)]
            if menu_param:
                menu_domain.append(('id', '=', menu_param))
            menu_ids = Menu.search(menu_domain)
        menu_data = []
        menu_ids = [_x for _x in menu_ids if _x > 0]
        for menu in Menu.browse(menu_ids):
            menu_data.append({'name': menu.name, 'id': menu.id, 'xml_id': xml_id(menu)})
            x_menu.add_row([menu.id, menu.name, menu.complete_name])
        if not menu_ids:
            menu_data.append({'name': '', 'id': '', 'xml_id': '', 'complete_name': ''})
        first_line = True
        for menu_line in menu_data:
            if first_line:
                x.add_row([action.name, action.id, xml_id(action), menu_line.get('name'), menu_line.get('id'),
                           menu_line.get('xml_id'), ])
                first_line = False
            else:
                x.add_row(['', '', '', menu_line.get('name'), menu_line.get('id'), menu_line.get('xml_id')])
    click.secho('')
    click.secho('Menus', fg='blue')
    echo(x_menu)
    click.secho('')
    click.secho('Action and menus XML-IDS', fg='blue')
    echo(x)

    for action in Action.browse(action_ids):
        click.secho('')
        click.secho('Associated views to the action : %s, xml-id : %s' % (action.name, xml_id(action)), fg='blue')
        click.secho('Context : %s' % action.context, fg='blue')
        click.secho('Domain : %s' % action.domain, fg='blue')
        associated_views = []
        x2 = PrettyTable()
        x2.field_names = ["View name", "View Type", "XML-ID"]
        for f in x2.field_names:
            x2.align[f] = 'l'
        if action.search_view_id:
            if not view_type_param or view_type_param == action.search_view_id.type:
                associated_views.append(action.search_view_id.id)
                blacklist.append(action.search_view_id.id)
        if action.view_id:
            if not view_type_param or view_type_param == action.view_id.type:
                associated_views.append(action.view_id.id)
                blacklist.append(action.view_id.id)
        for view in action.view_ids:
            if view.view_id:
                if not view_type_param or view_type_param == view.view_id.type:
                    associated_views.append(view.view_id.id)
                    blacklist.append(view.view_id.id)
        views = View.browse(list(set(associated_views)))
        for view in views:
            x2.add_row([view.name, view.type, xml_id(view)])
        echo(x2)

    click.secho('')
    click.secho('Other views', fg='blue')
    other_views = list(set(view_ids) - set(blacklist))
    views = View.browse(list(set(other_views)))
    x3 = PrettyTable()
    x3.field_names = ["View name", "View Type", "XML-ID"]
    for f in x3.field_names:
        x3.align[f] = 'l'
    for view in views:
        x3.add_row([view.name, view.type, xml_id(view)])
    echo(x3)


@cli.command()
@click.argument('field', type=click.STRING, required=True)
@click.argument('model', type=click.STRING, required=False)
@click.option('--type', type=click.STRING, required=False)
@click.pass_context
def search_field(ctx, field, model, type):
    """Searching for the views that contains the field"""
    click.echo('Search the field %s on the views of the model %s ' % (field, model))
    odoo = ctx.obj['action_login']()
    echo = ctx.obj['echo']
    xml_id = ctx.obj['xml_id']
    View = odoo.env['ir.ui.view']
    view_domain = [('arch_db', 'like', field)]
    if model:
        view_domain.append(('model', '=', model), )
    if type:
        view_domain.append(('type', '=', type), )
    view_ids = View.search(view_domain)
    views = View.browse(view_ids)
    x = PrettyTable()
    x.field_names = ["View name", "View Type", "Model", "XML-ID"]
    for f in x.field_names:
        x.align[f] = 'l'
    for view in views:
        x.add_row([view.name, view.type, view.model or '', xml_id(view)])
    echo(x)
    click.echo("Total : %s" % len(views))


@cli.command()
@click.argument('term', type=click.STRING, required=True)
@click.argument('lang', type=click.STRING, required=False)
@click.argument('module', type=click.STRING, required=False)
@click.option('--exact', is_flag=True, type=click.BOOL, default=False, required=False)
@click.pass_context
def trans_search(ctx, term, lang, module, exact):
    """Searching for the term in the translation table"""
    click.echo('Search for the term %s in the translation table' % term)
    odoo = ctx.obj['action_login']()
    echo = ctx.obj['echo']
    Translation = odoo.env['ir.translation']
    view_domain = []
    if lang:
        view_domain += [('lang', '=', lang)]
    if module:
        view_domain += [('module', '=', module)]
    if exact:
        view_domain += ['|', ('value', '=', term), ('src', '=', term)]
    else:
        view_domain += ['|', ('value', 'ilike', term), ('src', 'ilike', term)]
    item_ids = Translation.search(view_domain)
    items = Translation.browse(item_ids)
    x = PrettyTable()
    x.field_names = ["Src", "Value", "Module", "Lang", "Type", "Name"]
    for f in x.field_names:
        x.align[f] = 'l'
    for item in items:
        x.add_row([item.src, item.value, item.module, item.lang, item.type, item.name])
    echo(x)
    click.echo("Total : %s" % len(items))


@cli.command()
@click.argument('view', type=click.STRING, required=True)
@click.pass_context
def arch(ctx, view):
    """Cat the arch of the view"""
    click.echo('Show the arch of the view %s ' % view)
    odoo = ctx.obj['action_login']()
    object_from_xml_id = ctx.obj['object_from_xml_id']
    View = odoo.env['ir.ui.view']
    if view.isdigit():
        view_domain = [('id', '=', int(view))]
    else:
        view_xml_id = object_from_xml_id(view)
        if not view_xml_id:
            click.secho('XML-ID not found', fg='red')
            return
        view_domain = [('id', '=', view_xml_id.id)]
    view_ids = View.search(view_domain)
    views = View.browse(view_ids)
    for view in views:
        click.echo(view.arch)


@cli.command()
@click.argument('model', type=click.STRING, required=True)
@click.option('--fields', '-f', type=click.STRING, help='Fields to show', multiple=True)
@click.option('--domain', '-d', nargs=3, help='Filter the records', multiple=True)
@click.option('--limit', '-l', type=click.INT, default=0, help="Limit of records")
@click.option('--order', '-o', type=click.STRING, default='id asc', help="Expression to sort the records")
@click.option('--xmlid', is_flag=True, type=click.BOOL, default=False, help="Show XML-ID column")
@click.pass_context
def data(ctx, model, fields, domain, limit, order, xmlid):
    """Show the data of a model"""
    click.echo('Show the data of the model %s ' % model)
    final_domain = []
    if domain:
        for d in domain:
            field, operator, value = d
            try:
                value = eval(value)
            except:
                pass
            final_domain.append((field, operator, value))
    odoo = ctx.obj['action_login']()
    xml_id = ctx.obj['xml_id']
    echo = ctx.obj['echo']
    Model = odoo.env[model]
    fields = ['display_name'] if not fields else fields
    records = Model.search_read(final_domain or [], fields, limit=limit, order=order)
    if records:
        fields = records[0].keys()
    x = PrettyTable()
    if xmlid:
        x.field_names = fields + ['XML-ID']
    else:
        x.field_names = fields
    for f in x.field_names:
        x.align[f] = 'l'
    for record in records:
        y = [record.get(f) for f in fields]
        if xmlid:
            y += [xml_id(model, record.get('id'))]
        x.add_row(y)
    echo(x)


@cli.command()
@click.argument('model', type=click.STRING, required=True)
@click.option('--values', '-v', nargs=2, type=click.STRING, help='Values to apply', multiple=True)
@click.option('--domain', '-d', nargs=3, help='Filter the records', multiple=True)
@click.pass_context
def update_data(ctx, model, values, domain):
    """Update the data of a model"""
    click.echo('Update the data of the model %s ' % model)
    final_domain = []
    if domain:
        for d in domain:
            field, operator, value = d
            try:
                value = eval(value)
            except:
                pass
            final_domain.append((field, operator, value))
    _values = {}
    for _k, _v in values:
        try:
            _v = eval(_v)
        except:
            pass
        _values[_k] = _v
    values = _values
    odoo = ctx.obj['action_login']()
    Model = odoo.env[model]
    model_ids = Model.search(final_domain)
    if click.confirm('Are you sure you want to update %s records from %s with the values %s' % (
            len(model_ids), model, values)):
        success, error = 0, 0
        for model_id in model_ids:
            try:
                Model.write([model_id], values)
                click.secho('the record #%s is updated' % model_id, fg='green')
                success += 1
            except:
                click.secho('the record #%s can not be updated' % model_id, fg='red')
                error += 1
        click.echo('success: %s, error: %s' % (success, error))


@cli.command()
@click.argument('model', type=click.STRING, required=True)
@click.option('--domain', '-d', nargs=3, help='Filter the records', multiple=True)
@click.pass_context
def count(ctx, model, domain):
    """Count the records on a model"""
    click.echo('Count the number of records on the model %s ' % model)
    final_domain = []
    if domain:
        for d in domain:
            field, operator, value = d
            try:
                value = eval(value)
            except:
                pass
            final_domain.append((field, operator, value))
    odoo = ctx.obj['action_login']()
    echo = ctx.obj['echo']
    Model = odoo.env[model]
    nbr = Model.search_count(final_domain or [])
    x = PrettyTable()
    x.field_names = ['Count']
    x.align['Count'] = 'l'
    x.add_row([nbr])
    echo(x)


@cli.command()
@click.argument('model', type=click.STRING, required=True)
@click.option('--user', '-u', type=click.STRING, required=False, multiple=True)
@click.pass_context
def crud(ctx, model, user):
    """List users access to the givenmodel"""
    click.echo('List the users access to the model %s ' % model)
    click.secho('', fg='blue')
    click.secho('CRUD', fg='blue')
    odoo = ctx.obj['action_login']()
    echo = ctx.obj['echo']
    User = odoo.env['res.users']
    IrRule = odoo.env['ir.rule']
    IrModelAccess = odoo.env['ir.model.access']
    ir_rule_ids = IrRule.search([('model_id.model', '=', model)])
    rule_lines = IrRule.read(ir_rule_ids)
    ir_model_access_ids = IrModelAccess.search([('model_id.model', '=', model)])
    crud_lines = IrModelAccess.read(ir_model_access_ids)
    user_ids = User.search([]) if not user else User.search([('login', 'in', user)])
    x = PrettyTable()
    x.field_names = ["Name", "Read", "Write", "Create", "Unlink"]
    x.align["Name"] = "l"
    x.align["Read"] = x.align["Write"] = x.align["Create"] = x.align["Unlink"] = "c"
    for user in User.browse(user_ids):
        name = user.name
        group_ids = map(lambda r: r.id, user.groups_id)
        filtered_crud_lines = filter(lambda r: not r.get('group_id') or r.get('group_id')[0] in group_ids, crud_lines)
        create = write = unlink = read = False
        for crud_line in filtered_crud_lines:
            read = crud_line.get('perm_read', False) or read
            write = crud_line.get('perm_write', False) or write
            unlink = crud_line.get('perm_unlink', False) or unlink
            create = crud_line.get('perm_create', False) or create
        x.add_row([name, read and 'X' or '', write and 'X' or '', create and 'X' or '', unlink and 'X' or ''])
    echo(x)
    click.secho('', fg='blue')
    click.secho('Global domains', fg='blue')
    filtered_gloabl_rule_lines = filter(lambda r: r.get('global') == True, rule_lines)
    x2 = PrettyTable()
    x2.field_names = ["Domain", "Domain Force"]
    x2.align["Domain"] = x2.align["Domain Force"] = "l"
    for line in filtered_gloabl_rule_lines:
        x2.add_row([line.get('domain', ''), line.get('domain_force', '')])
    echo(x2)
    click.secho('', fg='blue')
    click.secho('Rules', fg='blue')
    x3 = PrettyTable()
    x3.field_names = ["Name", "Domain", "Domain force", "Read", "Write", "Create", "Unlink"]
    x3.align["Name"] = x3.align["Domain"] = "l"
    x3.align["Read"] = x3.align["Write"] = x3.align["Create"] = x3.align["Unlink"] = "c"
    for user in User.browse(user_ids):
        name = user.name
        group_ids = map(lambda r: r.id, user.groups_id)
        filtered_rule_lines = filter(
            lambda r: r.get('global') == False and set(r.get('groups')).intersection(group_ids), rule_lines)
        for rule_line in filtered_rule_lines:
            domain = rule_line.get('domain', '')
            domain_force = rule_line.get('domain_force', '')
            read = rule_line.get('perm_read', False)
            write = rule_line.get('perm_write', False)
            unlink = rule_line.get('perm_unlink', False)
            create = rule_line.get('perm_create', False)
            x3.add_row([name, domain, domain_force, read and 'X' or '', write and 'X' or '', create and 'X' or '',
                        unlink and 'X' or ''])
    echo(x3)


@cli.command()
@click.argument('model', type=click.STRING, required=True)
@click.option('--show', '-s', is_flag=True, type=click.BOOL, default=False)
@click.option('--duplicates', '-d', is_flag=True, type=click.BOOL, default=False)
@click.option('--fields', '-f', is_flag=True, type=click.BOOL, default=False)
@click.option('--buttons', '-b', is_flag=True, type=click.BOOL, default=False)
@click.option('--pages', '-b', is_flag=True, type=click.BOOL, default=False)
@click.option('--xpath', '-x', type=click.STRING, default='')
@click.option('--view_id', '-i', type=click.STRING, default=None)
@click.option('--view_type', '-d', type=click.STRING, default='form')
@click.option('--attrs', '-a', type=click.STRING, default=False, multiple=True)
@click.pass_context
def view(ctx, model, show, duplicates, fields, buttons, pages, xpath, view_id, view_type, attrs):
    """Execute fields_view_get on the given model
    Extract: duplicates, xpath, buttons, pages, etc"""
    if xpath:
        xpath = '//%s[@%s=\'%s\']' % tuple(xpath.split(' ')) if len(xpath.split(' ')) == 3 else '//%s' % xpath

    def node_attrs(node):
        _node_attrs = []
        for _k, _v in node.attrib.iteritems():
            if _k in attrs:
                _node_attrs.append('%s=%s' % (_k, _v))
        return '   '.join(_node_attrs)

    def parent_xpath(node, j, node_number):
        xpath_list = []
        first = True
        while True:
            tag = node.tag
            if node.get('name'):
                tag += '[@name=\'%s\']' % node.get('name')
            if node_number > 1 and first:
                tag += '[%s]' % (j + 1)
            xpath_list.append(tag)
            node = node.getparent()
            first = False
            if node is None:
                break
        return '//' + '/'.join(xpath_list[::-1])

    """Execute fields_view_get on the given model"""
    click.echo(
        'execute the function fields_view_get on the model %s with print=%s duplicates=%s' % (model, show, duplicates))
    odoo = ctx.obj['action_login']()
    echo = ctx.obj['echo']
    object_from_xml_id = ctx.obj['object_from_xml_id']
    Model = odoo.env[model]
    fvg_args = {'view_type': view_type}
    if view_id:
        view_id = int(view_id) if view_id.isdigit() else view_id
        view_id = object_from_xml_id(view_id).id if isinstance(view_id, basestring) else view_id
        fvg_args.update({'view_id': view_id})
    xml = Model.fields_view_get(**fvg_args).get('arch')
    root = etree.fromstring(xml)
    model_fields = [f.attrib['name'] for f in root.xpath('//field') if 'name' in f.attrib]
    _fields = []
    if duplicates:
        click.secho('', fg='blue')
        click.secho('Show duplicate fields', fg='blue')
        _duplicates = []
        for f in model_fields:
            if f in _fields:
                _duplicates.append(f)
            _fields.append(f)
        x1 = PrettyTable()
        x1.field_names = ["Name"]
        x1.align["Name"] = "l"
        for _d in _duplicates:
            x1.add_row([_d])
        echo(x1)
    if show:
        click.secho('', fg='blue')
        click.secho('Show XML', fg='blue')
        click.echo(etree.tostring(root, pretty_print=True, encoding='utf-8'))
    if fields:
        click.secho('', fg='blue')
        click.secho('Show fields', fg='blue')
        x2 = PrettyTable()
        x2.field_names = ["Name", "String", "Attributes"]
        x2.align["Name"] = x2.align["Attributes"] = x2.align["String"] = "l"
        for field_item in root.xpath('//field'):
            x2.add_row([field_item.attrib.get('name', ''), field_item.attrib.get('string', ''), node_attrs(field_item)])
        echo(x2)
    if buttons:
        click.secho('', fg='blue')
        click.secho('Show buttons', fg='blue')
        x3 = PrettyTable()
        x3.field_names = ["Name", "String", "Attributes"]
        x3.align["Name"] = x3.align["Attributes"] = x3.align["String"] = "l"
        for field_item in root.xpath('//button'):
            x3.add_row([field_item.attrib.get('name', ''), field_item.attrib.get('string', ''), node_attrs(field_item)])
        echo(x3)
    if pages:
        click.secho('', fg='blue')
        click.secho('Show pages', fg='blue')
        x4 = PrettyTable()
        x4.field_names = ["Name", "String", "Attributes"]
        x4.align["Name"] = x4.align["Attributes"] = x4.align["String"] = "l"
        for field_item in root.xpath('//page'):
            x4.add_row([field_item.attrib.get('name', ''), field_item.attrib.get('string', ''), node_attrs(field_item)])
        echo(x4)
    if xpath:
        click.secho('', fg='blue')
        click.secho('Show XPATH', fg='blue')
        x5 = PrettyTable()
        x5.field_names = ["Tag", "Name", "String", "Parent XPATH"]
        x5.align["Tag"] = x5.align["Name"] = x5.align["Parent XPATH"] = x5.align["String"] = "l"
        nbr = len(root.xpath(xpath)) if root.xpath(xpath) is not None else 0
        for i, node_xpath in enumerate(root.xpath(xpath)):
            if show:
                click.echo(etree.tostring(node_xpath, pretty_print=True, encoding='utf-8'))
            else:
                x5.add_row([node_xpath.tag, node_xpath.attrib.get('name', ''), node_xpath.attrib.get('string'),
                            parent_xpath(node_xpath, i, nbr)])
        if not show:
            echo(x5)


if __name__ == '__main__':
    cli(obj={})


def main():
    return cli(obj={})
