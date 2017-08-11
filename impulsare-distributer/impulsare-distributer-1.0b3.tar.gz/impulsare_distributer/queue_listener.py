#!/usr/bin/env python
import click

from redis import Redis
from rq import Connection, Worker


@click.command(help='''
Start an impulsare worker

In case of error, try ``queue-listener --debug -c my_config.yml``
''', name='queue-listener')
@click.option('--debug/--no-debug', '-d', default=False)
@click.option('--host', '-h', required=True, help='Host')
@click.option('--port', '-p', default=6379, help='Redis Port')
@click.option('--queue', '-q', required=True, help='Queue to listen')
def cli(debug: bool, host: str, port: int, queue: str):
    with Connection(Redis(host, port)):
        Worker(queue).work()


def main():
    try:
        cli()
    except Exception as e:
        import sys
        if '--debug' in sys.argv or '-d' in sys.argv:
            raise e

        print(click.style(str(e), fg='red'), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
