from .application import Application
from .config import Config
from .logger import Logger
import builtins
import click

@click.command(context_settings=Config.context())
@click.option('-c', '--clear', default=False, is_flag=True, help='Clear all tags before writing.')
@click.option('-m', '--match', default=False, is_flag=True, help='Match and import existing files.')
@click.option('-o', '--output', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True), help='Download directory.', metavar='<directory>')
@click.option('-p', '--preview', default=False, is_flag=True, help='Preview download and tagging output.')
@click.option('-q', '--quiet', default=False, is_flag=True, help='Disable stdout logging.')
@click.option('-r', '--rename', default=False, is_flag=True, help='Rename episodes with XML data.')
@click.option('-s', '--subdir', default=False, is_flag=True, help='Generate subdirectory for downloading.')
@click.option('-t', '--tag', default=False, is_flag=True, help='Tag episodes with XML data.')
@click.option('-v', '--verbose', default=False, is_flag=True, help='Enable verbose logging.')

@click.option('--drop', default=False, is_flag=True, help='Empty database.')
@click.option('--limit', default=0, type=int, help='Episode download limit.', metavar='<int>')
@click.option('--offline', default=False, is_flag=True, help='Import only mode.')
@click.option('--offset', default=0, type=int, help='Episode download offset.', metavar='<int>')
@click.option('--order', default='desc', show_default=True, type=click.Choice(['asc', 'desc']), help='Episode download order.')
@click.option('--purge', default=False, is_flag=True, help='Empty destination folder.')

@click.option('--track-src', default='index', show_default=True, type=click.Choice(['index', 'release']), help='Source for track tag.')
@click.option('--image-src', default='podcast', show_default=True, type=click.Choice(['episode', 'podcast']), help='Source for image tag')
@click.option('--album', help='Override album tag.', metavar='<string>')
@click.option('--albumartist', help='Override album artist tag.', metavar='<string>')
@click.option('--artist', help='Override artist tag.', metavar='<string>')
@click.option('--comment', help='Override comment tag.', metavar='<string>')
@click.option('--composer', help='Override composer tag.', metavar='<string>')
@click.option('--genre', help='Override genre tag.', metavar='<string>')
@click.option('--image', type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=True), help='Override image tag.', metavar='<file>')

@click.argument('source', type=str)
def cli(**kwargs):
  if Config.validate():
    builtins.ui = {k: v for k, v in kwargs.items() if v}
    builtins.logger = Logger(ui)
    return Application.run()

def main():
  cli(obj={})

if __name__ == '__main__':
  main()