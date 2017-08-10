# -*- coding: utf-8 -*-

"""Console script for pyliveleak."""
import logging

import pyliveleak
import click

existing_file = click.Path(exists=True, file_okay=True, dir_okay=False)


@click.option('--path', required=True, help='The video to upload', type=existing_file)
@click.option('--username', required=True, help='Your liveleak.com username')
@click.option('--password', required=True, help='Your liveleak.com password')
@click.option('--loglevel', default=logging.INFO)
@click.command()
def main(path, username, password, loglevel):
    """Console script for pyliveleak."""
    logging.basicConfig(level=loglevel)
    index_page = pyliveleak.login(username, password)
    file_token, item_token = index_page.add_item(path)
    click.echo('https://www.liveleak.com/view?i=%s' % item_token)


if __name__ == "__main__":
    main()
