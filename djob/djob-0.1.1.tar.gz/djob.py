#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os
import re
from os.path import expanduser
import click
import subprocess

import time

from click import style
from configobj import ConfigObj


def mysecho(text, file=None, nl=True, err=False, color=None, silent=False, **styles):
    if not silent:
        click.echo(style(text, **styles), file=file, nl=nl, err=err, color=color)


click.secho = mysecho

__VERSION__ = '0.1.1'
__AUTHOR__ = ''
__WEBSITE__ = ''
__DATE__ = ''

home = expanduser("~")
home = os.path.join(home, '.dyvz')
JOBS_FILE = os.path.join(home, 'jobs.ini')

try:
    os.makedirs(home)
except:
    pass

if not os.path.exists(JOBS_FILE):
    with codecs.open(JOBS_FILE, mode='w+', encoding='utf-8') as config_file:
        pass


@click.group()
@click.version_option(__VERSION__, is_flag=True, expose_value=False, is_eager=True, help="Show the version")
@click.pass_context
def cli(ctx):
    """CLI for Djob"""
    config_job_obj = ConfigObj(JOBS_FILE, encoding='utf-8')
    ctx.obj['config_job_obj'] = config_job_obj
    jobs = {}
    for job_section in config_job_obj.sections:
        job_list = [(x, config_job_obj[job_section][x]) for x in config_job_obj[job_section]]
        job_list = sorted(job_list, key=lambda (x, y): x)
        jobs[job_section] = job_list
    ctx.obj['jobs'] = jobs


@cli.command()
@click.argument('job_name', type=click.STRING, required=True)
@click.pass_context
def create(ctx, job_name):
    """Create a new job"""
    config = ctx.obj['config_job_obj']
    click.echo('Create new job %s to the config %s' % (job_name, config.filename))
    if job_name not in config.sections:
        config[job_name] = {}
    else:
        click.secho('The job %s already exists' % job_name, fg='red')
        return
    index = 0
    while True:
        index += 1
        cmd = click.prompt('Command %s' % index, type=unicode)
        key = 'command%s' % index
        if click.confirm('Save ?'):
            config[job_name][key] = cmd
            continue
        else:
            break
    config.write()
    click.secho('The job %s is created' % job_name, fg='green')


@cli.command()
@click.argument('job_name', type=click.STRING, required=False)
@click.pass_context
def update(ctx, job_name):
    """Update a job"""
    config = ctx.obj['config_job_obj']
    click.echo('Update the job %s from the config %s' % (job_name, config.filename))
    if job_name not in config.sections:
        click.secho('The job %s not found.' % job_name, fg='red')
        return
    index = 0
    while True:
        index += 1
        key = 'command%s' % index
        default = config[job_name][key] if key in config[job_name] else 'New command !!'
        cmd = click.prompt('Command %s' % index, default=default, type=unicode)
        if click.confirm('Save ?'):
            config[job_name][key] = cmd
            continue
        else:
            break
    config.write()
    click.secho('The job %s is updated' % job_name, fg='green')


@cli.command()
@click.argument('jobs', type=click.STRING, required=True, nargs=-1)
@click.pass_context
def delete(ctx, jobs):
    """Delete a job"""
    config = ctx.obj['config_job_obj']
    click.echo('Delete the jobs %s from the config %s' % (jobs, config.filename))
    for job_name in jobs:
        if job_name not in config.sections:
            click.secho('The job %s not found.' % job_name, fg='red')
        else:
            del config[job_name]
            click.secho('The job %s is removed' % job_name, fg='green')
    config.write()


@cli.command()
@click.argument('jobs', type=click.STRING, required=False, nargs=-1)
@click.option('--commands', '-c', is_flag=True, default=False)
@click.pass_context
def list(ctx, jobs, commands):
    """List jobs"""
    all_jobs = ctx.obj['jobs']
    for job_name, job_values in all_jobs.iteritems():
        if not jobs or job_name in jobs:
            click.secho('JobName : %s' % job_name, fg='blue')
            if commands:
                for cmd_key, cmd_value in job_values:
                    cmd_key = cmd_key.replace('command', '')
                    click.secho("{:>4} : {}".format(cmd_key, cmd_value))
                click.echo()


def process_time(ctx, name, value):
    sleep = 0
    pattern = re.compile('(\d+)([smh])')
    values = re.findall(pattern, value)
    for number, ttype in values:
        if number and ttype:
            number = int(number)
            if ttype == 's':
                sleep += number
            if ttype == 'm':
                sleep += number * 60
            if ttype == 'h':
                sleep += number * 60 * 60
    if not sleep:
        return (0, '')
    hours = sleep / (60 * 60)
    minutes = (sleep - hours * 60 * 60) / 60
    seconds = (sleep - hours * 60 * 60 - minutes * 60)
    return (sleep, '%s hours %s minutes %s seconds' % (hours, minutes, seconds))


def __execute_commands(commands):
    for command in commands:
        click.secho('Command : %s' % command, fg='cyan')
        p = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        out, err = p.communicate()
        if err:
            click.secho(err, fg='red')
        if out:
            click.secho(out, fg='green')


@cli.command()
@click.argument('jobs', nargs=-1, type=click.STRING, required=True, )
@click.option('--after', '-a', type=click.STRING, default='', required=False, callback=process_time)
@click.option('--sleep', '-s', type=click.STRING, default='', required=False, callback=process_time)
@click.option('--number', '-n', type=click.INT, default=1, required=False)
@click.option('--clear', '-c', is_flag=True, default=False,  )
@click.pass_context
def run(ctx, jobs, sleep, after, number, clear):
    """Show jobs"""
    commands = []
    all_jobs = ctx.obj['jobs']
    for job in jobs:
        if os.path.isfile(job):
            with codecs.open(job, encoding='utf8', mode='r') as job_file:
                for line in job_file.readlines():
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith('#') or line.startswith(';') or line.startswith('//'):
                        continue
                    commands.append(line)
        elif job in all_jobs:
            for cmd_key, cmd_value in all_jobs.get(job):
                if cmd_value:
                    commands.append(cmd_value.strip())
        else:
            click.secho('Can not found the job %s' % job, fg='red')
            return
    if sleep[0] and number == 1:
        click.secho('Give a number great than 1 or -1 for unlimit execution', fg='red')
        return
    if after[0]:
        click.secho('Sleep %s' % after[1], fg='yellow')
        time.sleep(after[0])
    if sleep[0]:
        click.secho('Execute commands every %s' % sleep[1], fg='yellow')
    index = 0
    while True:
        index += 1
        if index > number > 0:
            break
        if clear:
            click.clear()
        click.echo()
        click.secho('-' * 50, fg='blue')
        click.secho('Iteration {:>4} : Sleep {}'.format(index, sleep[1]), fg='blue')
        __execute_commands(commands)
        if sleep[0]:
            if (index + 1) > number > 0:
                break
            click.secho('Waiting ..... sleep {}'.format(sleep[1]), fg='blue')
            time.sleep(sleep[0])


if __name__ == '__main__':
    cli(obj={})


def main():
    return cli(obj={})
