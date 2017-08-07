import logging

import click


logger = logging.getLogger(__name__)


@click.command('select', short_help="Select atoms from a PDB file.")
@click.argument("pdb_file", type=click.File(mode='r'))
@click.option("--selection")
def cli(pdb_file, selection):
    raise NotImplementedError
