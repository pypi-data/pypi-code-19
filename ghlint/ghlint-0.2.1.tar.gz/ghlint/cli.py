import click
from ghlint import run
from . import config


@click.command()
def main():
    settings = config.settings()
    run(settings)
    return

if __name__ == '__main__':
    main()
