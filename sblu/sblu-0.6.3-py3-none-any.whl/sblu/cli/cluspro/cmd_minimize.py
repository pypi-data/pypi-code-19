import os
import sys
import json
import logging
from subprocess import check_call
from tempfile import mkstemp

import click
from path import Path

from sblu import PRMS_DIR
from sblu.util import which

logger = logging.getLogger(__name__)


@click.command('minimize', help="Minimize all members of a cluster.")
@click.option('--prm', type=click.Path(exists=True),
              default=PRMS_DIR/'charmm_params.prm')
@click.option('--rtf', type=click.Path(exists=True),
              default=PRMS_DIR/'charmm_params.rtf')
@click.option('--atoms-prm', type=click.Path(exists=True),
              default=PRMS_DIR/'atoms.0.0.6.prm.ms.3cap+0.5ace.Hr0rec')
@click.option('-o', '--output-prefix', type=click.Path())
@click.argument('rec_pdb', type=click.Path(exists=True))
@click.argument('rec_psf', type=click.Path(exists=True))
@click.argument('lig_pdb', type=click.Path(exists=True))
@click.argument('lig_psf', type=click.Path(exists=True))
@click.argument('clusters', type=click.Path(exists=True))
@click.argument('ftfile', type=click.Path(exists=True))
@click.argument('rotations', type=click.Path(exists=True))
def cli(rec_pdb, rec_psf, lig_pdb, lig_psf,
        prm, rtf, atoms_prm, output_prefix,
        clusters, ftfile, rotations):
    refine_bin = which('complex_refine', required=True)
    logger.info('using complex refine {}'.format(refine_bin))
    logger.info('atoms_prm: {}'.format(atoms_prm))

    try:
        with open(clusters, 'r') as f:
            cluster_centers = set(cluster['center'] for cluster in json.load(f)['clusters'])
    except:
        with open(clusters) as f:
            cluster_centers = set()
            for l in f:
                if l.startswith('Center'):
                    cluster_centers.add(int(l.split()[1]) - 1)

    if len(cluster_centers) == 0:
        logger.warning('No cluster centers found')
        sys.exit(1)

    tmp_fd, tmp_filepath = mkstemp(text=True)
    with open(ftfile, "r") as ifp, os.fdopen(tmp_fd, "w") as ofp:
        for i, l in enumerate(ifp):
            if i in cluster_centers:
                ofp.write(l)

    try:
        cmd = [refine_bin]
        if output_prefix is not None:
            output_dir = os.path.dirname(output_prefix)
            if output_dir:
                Path(output_dir).mkdir_p()
            cmd += ['-o', output_prefix]
        cmd += [prm, rtf, atoms_prm]
        cmd += [rec_pdb, rec_psf, lig_pdb, lig_psf]
        cmd += [tmp_filepath, rotations]

        logger.info(' '.join(cmd))
        check_call(cmd)
    except:
        logger.error(
            "error running complex_refine: temporary ftfile located at {}".format(tmp_filepath))
        raise
    else:
        os.unlink(tmp_filepath)
