import base
import click

#COLUMN HELPS
h_column_help = 'A comma-separated list of column names'
format_column_help = '''
The unit in which to display byte values, valid choices are:
\'b\', \'k\', \'kb\', \'m\', \'mb\', \'g\', \'gb\', \'t\', \'tb\', \'p\', \'pb\'
'''
index_column_help = '''A comma-separated list of index
names to limit the returned information'''
repository_column_help='''
Name of the repository
'''
action_column_help = 'List of comma-separated actions to be returned'
name_column_help = 'List of aliases names'
node_column_help = 'A comma-separated list of node IDs or names to limit the returned information'
detailed_column_help = 'Return detailed task information'

#COMMAND HELPS
fielddata_help = '''Shows information about currently loaded fielddata on a per-node basis.'''
indices_help = 'The indices command provides a cross-section of each index.'
allocation_help = 'Information about shard allocation'
count_help = 'Count of the documents stored in index'
health_help = 'Information regarding health of the cluster'
nodeattrs_help = 'Command shows custom node attributes'
nodes_help = 'The nodes command shows the cluster topology.'
recovery_help = 'recovery is a view of shard replication'
repositories_help='The repositories command shows the snapshot repositories registered in the cluster'
segments_help='The segments command is the detailed view of Lucene segments per index.'
shards_help='The shards command is the detailed view of what nodes contain which shards.'
snapshots_help='The snapshots command shows all snapshots that belong to a specific repository'

@click.group()
def cat():
    '''
    Implementation of Cat APIs of Elasticsearch
    '''
    pass


@cat.command('allocation', short_help=allocation_help)
@click.option('--node', nargs=1, help=node_column_help)
@click.option('-h', nargs=1, help=h_column_help)
@click.option('--format', default='mb', help=format_column_help)
def allocation(node,format,h):
    '''
    Allocation provides a snapshot of how shards have located around the
    cluster and the state of disk usage
    '''
    try:
        response = base.es.cat.allocation(node_id=node,bytes=format, h=h, format='json')
        table = base.draw_table(response)
    except Exception as e:
        click.echo(e)
    else:
        click.echo(table)


@cat.command('count', short_help=count_help)
@click.option('--index', nargs=1, help=index_column_help)
@click.option('-h', nargs=1, help=h_column_help)
def count(index,h):
    '''
    Gives count of the documents stored in Elasticsearch. If index option is
    provided, it will provide document count of that index.
    '''
    try:
        response = base.es.cat.count(index,h=h)
        table = base.draw_table(response)
    except Exception as e:
        click.echo(e)
    else:
        click.echo(table)

@cat.command('fielddata', short_help=fielddata_help)
@click.option('--fields', nargs=1, help='''A comma-separated list of fields to
return the fielddata size
''')
@click.option('--format', default='mb', help=format_column_help)
@click.option('-h', nargs=1, help=h_column_help)
def fielddata(fields,format,h):
    try:
        response = base.es.cat.fielddata(fields=fields,bytes=format,h=h, format='json')
        table = base.draw_table(response)
    except Exception as e:
        click.echo(e)
    else:
        click.echo(table)


@cat.command('health', short_help=health_help)
@click.option('-h', nargs=1, help=h_column_help)
def health(h):
    try:
        response = base.es.cat.health(h=h, format='json')
        table = base.draw_table(response)
    except Exception as e:
        click.echo(e)
    else:
        click.echo(table)


@cat.command('indices', short_help= indices_help)
@click.option('--index', nargs=1, help=index_column_help)
@click.option('-h', nargs=1, help=h_column_help)

def indices(index,h):
    '''
    The indices command provides a cross-section of each index.
    This information spans nodes.
    We can tell quickly how many shards make up an index,
    the number of docs, deleted docs, primary store size,
    and total store size (all shards including replicas).
    All these exposed metrics come directly from Lucene APIs.
    '''
    try:
        response = base.es.cat.indices(index, h=h, format='json')
        table = base.draw_table(response)
    except Exception as e:
        click.echo(e)
    else:
        click.echo(table)




@cat.command('nodeattrs', short_help=nodeattrs_help)
@click.option('-h', nargs=1, help=h_column_help)
def nodeattrs(h):
    try:
        response = base.es.cat.nodeattrs(h=h, format='json')
        if not response:
            click.echo("No attributes as of now")
            return
        table = base.draw_table(response)
    except Exception as e:
        click.echo(e)
    else:
        click.echo(table)


@cat.command('nodes', short_help=nodes_help)
@click.option('-h', nargs=1, help=h_column_help)
def nodes(h):
    try:
        response = base.es.cat.nodes(h=h, format='json')
        if not response:
            click.echo("No Nodes as of now")
            return
        table = base.draw_table(response)
    except Exception as e:
        click.echo(e)
    else:
        click.echo(table)



@cat.command('recovery', short_help=recovery_help)
@click.option('--index', nargs=1, help=index_column_help)
@click.option('-h', nargs=1, help=h_column_help)
@click.option('--format', default='mb', help=format_column_help)
def recovery(index,format,h):
    try:
        response = base.es.cat.recovery(index=index,bytes=format, h=h, format='json')
        table = base.draw_table(response)
    except Exception as e:
        click.echo(e)
    else:
        click.echo(table)

@cat.command('repositories', short_help=repositories_help)
@click.option('-h', nargs=1, help=h_column_help)
def repositories(h):
    try:
        response = base.es.cat.repositories(h=h, format='json')
        if not response:
            click.echo("No Repositories as of now")
            return
        table = base.draw_table(response)
    except Exception as e:
        click.echo(e)
    else:
        click.echo(table)

@cat.command('segments', short_help=segments_help)
@click.option('--index', nargs=1, help=index_column_help)
@click.option('-h', nargs=1, help=h_column_help)
def segments(index,h):
    try:
        response = base.es.cat.segments(index=index, h=h, format='json')
        if not response:
            click.echo("No Segments present")
            return
        table = base.draw_table(response)
    except Exception as e:
        click.echo(e)
    else:
        click.echo(table)

@cat.command('shards', short_help=shards_help)
@click.option('--index', nargs=1, help=index_column_help)
@click.option('-h', nargs=1, help=h_column_help)
def shards(index,h):
    try:
        response = base.es.cat.shards(index=index, h=h, format='json')
        if not response:
            click.echo("No Shards present")
            return
        table = base.draw_table(response)
    except Exception as e:
        click.echo(e)
    else:
        click.echo(table)


@cat.command('snapshots', short_help=snapshots_help)
@click.option('--repository', nargs=1, help=repository_column_help)
@click.option('-h', nargs=1, help=h_column_help)
def snapshots(repository,h):
    try:
        response = base.es.cat.snapshots(repository=repository, h=h, format='json')
        if not response:
            click.echo("No snapshots present")
            return
        table = base.draw_table(response)
    except Exception as e:
        click.echo(e)
    else:
        click.echo(table)
