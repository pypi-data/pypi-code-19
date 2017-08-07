import logging
from subprocess import run, PIPE

import click
from path import Path

from sblu.util import which

logger = logging.getLogger(__name__)

FFTW_PLAN_TYPES = (
    'FFTW_ESTIMATE',
    'FFTW_MEASURE',
    'FFTW_PATIENT',
    'FFTW_EXHAUSTIVE'
)

OPTIONS = (
    ()
)
DEFAULTS = [
    '-T', "FFTW_EXHAUSTIVE",
    '-t', "1",
    '-c', '1.0',
    '--msur_k', '1.0',
    '--maskr', '1.0',
    '-k', '4'
]


@click.command('piper', help="Helpful wrapper for PIPER with sensible defaults.")
@click.option('--piper-path', type=click.Path(exists=True, readable=True))
@click.option('-p', '--atmprm', type=click.Path(exists=True), default='atoms.prm')
@click.option('-f', '--coeffs', type=click.Path(exists=True), default='coeffs.prm')
@click.option('-r', '--rotprm', type=click.Path(exists=True), default='rots.prm')
@click.option('n_rotations', '-R', type=click.INT, default=-1)
@click.option("n_eigenvectors", '-k', type=click.INT, default=4)
@click.option("n_translations_per_rotation", '-n', type=click.INT, default=1)
@click.option("fftw_plan_type", '-T', type=click.Choice(FFTW_PLAN_TYPES), default='FFTW_ESTIMATE')
@click.option("--print-grids/--no-print-grids", default=False)
@click.option('-O', '--output-dir', type=click.Path())
@click.argument('rec', type=click.Path(exists=True))
@click.argument('lig', type=click.Path(exists=True))
def cli(rec, lig,
        piper_path,
        atmprm, coeffs, rotprm,
        n_rotations, n_eigenvectors, n_translations_per_rotation,
        print_grids,
        output_dir):
    piper_bin = which(piper_path, required=True)
    logger.info('using piper {}'.format(piper_bin))

    cmd = [piper_bin]
    cmd += DEFAULTS
    if n_rotations is not None:
        cmd += ['-R', str(n_rotations)]
    if output_dir is not None:
        Path(output_dir).mkdir_p()
        cmd += ['-O', output_dir]
    cmd += ['-p', atmprm]
    cmd += ['-f', coeffs]
    cmd += ['-r', rotprm]
    cmd += [rec, lig]

    logger.info(' '.join(cmd))
    output = run(cmd, universal_newlines=True, stdout=PIPE, stderr=PIPE)
