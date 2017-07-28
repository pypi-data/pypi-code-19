import click
from .commands.encoding import encoding
from .commands.esub import esub
from .commands.run import run, rune

@click.group()
def main():
    pass


main.add_command(encoding)
main.add_command(esub)
main.add_command(run)
main.add_command(rune)

if __name__ == '__main__':
    main()
