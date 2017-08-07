import logging

import click

logger = logging.getLogger(__name__)


@click.command('psfgen', short_help="Helpful wrapper for psfgen")
@click.argument("segments", nargs=-1, type=click.Path(exists=True))
@click.option("--link")
@click.option("--first")
@click.option("--last")
@click.option("--smod", default="")
@click.option("--wdir")
@click.option("--psfgen", default="psfgen")
@click.option("--nmin", default="nmin")
@click.option("--prm")
@click.option("--rtf")
@click.option("--auto-disu/--no-auto-disu", default=True)
@click.option("--xplor-psf/--no-xplor-psf", default=False)
@click.option("--osuffix")
def cli(segments, psfgen, nmin):
    """Generate a PSF file from pdb files"""
    raise NotImplementedError
