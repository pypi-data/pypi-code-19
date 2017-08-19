# -*- coding: utf-8 -*-

import os
import click
from slugify import slugify
from jinja2 import Environment 
from jinja2 import FileSystemLoader
from pkg_resources import resource_filename
from sqlalchemy import create_engine
import logging

logger = logging.getLogger('__name__')


def to_dict(engine):
    '''
    Convert database table to a Pythonic structure

    Parameters
    ----------
    engine:sqlalchemy.engine.Engine

    Returns
    -------
    dict
        keys are table name 'slugified'
        values are a list of dict
    '''
    result = {}
    cnx = engine.connect()
    for table in engine.table_names():
        slug = slugify(table, to_lower=True, separator='_')
        result[slug] = [dict(row)
                        for row in cnx.execute(f'select * from {table}')]
    return result


def to_html(rows, title, _id='data', _class='table'):
    '''
    records rows to html

    Parameters
    ----------
    rows:records.rows
    _title:str
    _id:str
    _class:str

    Returns
    -------
    str
        html as text
    '''
    template_dir = resource_filename('db2table', 'templates')
    template = 'table.html'
    # FIXME:header as a variable ?
    try:
        header = list(rows[0].keys())
    except IndexError as e:
        logger.error(e)
        raise ValueError('rows should contains at least one row')
    env = Environment(loader=FileSystemLoader(template_dir), trim_blocks=True)
    return env.get_template(template).render({'data': rows,
                                              'title': title,
                                              '_id': _id,
                                              'table_class': _class,
                                              'header': header})


@click.command()
@click.argument('db_path', type=click.Path(exists=True))
@click.argument('folder', type=click.Path(exists=True))
def cli(db_path, folder):
    """
    Convert sqlite db to html : one file per table
    """
    engine = create_engine(f'sqlite:///{db_path}')
    for table, rows in to_dict(engine).items():
        with open(os.path.join(folder, f'{table}.html'), 'w') as fd:
            fd.write(to_html(rows, table))


if __name__ == "__main__":
    cli()
