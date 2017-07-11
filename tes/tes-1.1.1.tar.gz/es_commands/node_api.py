import base
import click

#COLUMN HELPS

#COMMAND HELPS
info_help = 'The cluster nodes info API allows to retrieve one or more (or all) of the cluster nodes information'
stats_help = 'The cluster nodes stats API allows to retrieve one or more (or all) of the cluster nodes statistics.'


@click.group()
def node():
    '''
    Implementation of Cluster Nodes APIs of Elasticsearch
    '''
    pass

@node.command('info', short_help=info_help)
def info():
    try:
        response = base.es.nodes.info()
    except Exception as e:
        click.echo(e)
    else:
        base.pretty_print(response)

@node.command('stats', short_help=stats_help)
def stats():
    try:
        response = base.es.nodes.stats()
    except Exception as e:
        click.echo(e)
    else:
        base.pretty_print(response)
