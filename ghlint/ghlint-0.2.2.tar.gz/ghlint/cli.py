import click
from . import config
from . import lint


@click.command()
def main():
    settings = config.settings()
    lint.run(settings)
    return

if __name__ == '__main__':
    main()
