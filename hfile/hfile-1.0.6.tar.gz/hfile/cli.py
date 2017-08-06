__author__ = 'Angus Yang'

from .walkdirectory import walkdirectory
from .filterbymtime import filterbymtime
from .removefile import removefile
import click
import json
import logging
import logging.handlers

# configure logger

logger = logging.getLogger("hfile")
logger.setLevel(logging.DEBUG)

# create the logging file handler
fh = logging.handlers.RotatingFileHandler("/var/log/hfile.log", maxBytes=20*1024*1024*200,
                                          backupCount=3)
# fh = logging.FileHandler("/var/log/hfile")
fmt = '%(asctime)s  %(name)s    %(levelname)s   %(message)s'
formatter = logging.Formatter(fmt)
fh.setFormatter(formatter)

# add handler to logger object
logger.addHandler(fh)


@click.group()
@click.pass_context
def main(context):
    """
    handles file by modify time
    """
    context.obj = {
    }


@main.command()
@click.argument('paths', nargs=-1)
@click.option('--beforehours', default=720, type=int,
              help='which files modify before configure hours')
@click.option('--extension', default='log',
              help="which files extension should be handle, Eg: --extension 'log,tar.gz'")
@click.option('--remove', is_flag=True, default=False,
              help="remove files")
@click.pass_context
def check(context, paths, beforehours, extension, remove):
    """
    check files by your ways
    """
    logger.info("Begin handle file")
    mutfileslist = list()
    try:
        for path in paths:
            mutfileslist.extend(walkdirectory(path))
        extension_tuple = tuple([str.strip() for str in extension.split(',')])
        checkedfilelists = list(
            filter(lambda x: filterbymtime(x, beforehours=beforehours, extension_tuple=extension_tuple), mutfileslist))
        filescount = len(checkedfilelists)
        result = {
            'filespathlist': checkedfilelists,
            'paths': paths,
            'untilnow_hours': beforehours,
            'filescount': filescount,
            'filesextension': extension_tuple
        }
        click.echo(json.dumps(result, indent=4, sort_keys=True))
        logger.info(result)
        if remove:
            list(map(removefile, checkedfilelists))
            click.secho('selected {} files has been removed'.format(filescount), fg='green')
            logger.info('selected {} files has been removed'.format(filescount))
        return checkedfilelists
        logger.info('complete handle files')
    except Exception as e:
        logger.exception("Occur a Error : ")
