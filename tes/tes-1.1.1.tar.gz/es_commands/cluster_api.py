import base
import click

#COLUMN HELPS
health_level_help ='''specify level: cluster, indices(Default: cluster).
Shards level is not supported as of now.
'''
index_column_help='''A comma-separated list of index names;
use _all or empty string to perform the
operation on all indices
'''

#COMMAND HELPS
health_help = 'Get a very simple status on the health of the cluster.'
state_help = 'Get a comprehensive state information of the whole cluster.'
stats_help = 'The Cluster Stats API allows to retrieve statistics from a cluster wide perspective'
get_settings_help = 'Get cluster settings.'


@click.group()
def cluster():
    '''
    Implementation of Cluster APIs of Elasticsearch
    '''
    pass


@cluster.command('health', short_help=health_help)
@click.option('--level', nargs=1, help=health_level_help)
def health(level):
    try:
        response = base.es.cluster.health(level=level)
        indices = None
        if(level == 'indices'):
            indices = response.pop('indices')
        table = base.draw_single_response_table(response)
        click.echo(table)
        if indices:
            for index in indices.keys():
                click.echo("Index is :"+index)
                click.echo(base.draw_single_response_table(indices[index]))
    except Exception as e:
        click.echo(e)


@cluster.command('state', short_help=state_help)
@click.option('--index', nargs=1, help=index_column_help)
def state(index):
    try:
        response = base.es.cluster.state(index=index)
        # table = base.draw_table(response)
    except Exception as e:
        click.echo(e)
    else:
        base.pretty_print(response)

@cluster.command('stats', short_help=stats_help)
def stats():
    try:
        response = base.es.cluster.stats(human=True)
        # table = base.draw_table(response)
    except Exception as e:
        click.echo(e)
    else:
        base.pretty_print(response)


@cluster.command('get_settings', short_help=get_settings_help)
def get_settings():
    try:
        response = base.es.cluster.get_settings()
    except Exception as e:
        click.echo(e)
    else:
        base.pretty_print(response)
