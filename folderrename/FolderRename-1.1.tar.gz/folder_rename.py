import click
import os

@click.group()
def cli():
    pass

@click.command()
@click.argument('dir_path', type=click.Path())
@click.argument('remove', default=' ')
def renamedir(dir_path, remove):
    ''' Rename the folders in given directory by replacing occurences of remove argument '''
    click.echo(dir_path)
    abs_path = os.path.abspath(dir_path)
    click.echo(abs_path)
    for fn in os.listdir(abs_path):
        os.rename(os.path.join(abs_path, fn),
            os.path.join(abs_path, fn.replace(remove, "")))

@click.command()
@click.argument('dir_path', type=click.Path())
@click.argument('not_contain', default=' ')
def delfile(dir_path, not_contain):
    abs_path = os.path.abspath(dir_path)
    click.echo(abs_path)
    for fn in os.listdir(abs_path):
        path = os.path.join(abs_path, fn)
        if os.path.isdir(path):
            for filename in os.listdir(path):
                if not_contain not in filename:
                    os.remove(os.path.join(path, filename))

cli.add_command(renamedir)
cli.add_command(delfile)
