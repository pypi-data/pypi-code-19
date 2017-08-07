import os
import logging
from subprocess import check_call

import click
from path import Path

from sblu import PRMS_DIR

logger = logging.getLogger(__name__)


def prepare(pdb, rtf, prm, prefix):
    cmd = ['sblu', 'pdb', 'prep']
    cmd += ['--rtf', rtf]
    cmd += ['--prm', prm]
    cmd += ['--out-prefix', prefix]
    cmd += [pdb]

    logger.info(' '.join(cmd))
    check_call(cmd)


def run_enzyme(rec, lig, charmm_rtf, charmm_prm, rotations,
               output_dir):
    atoms_prm = PRMS_DIR/'atom'/'atoms.0.0.6.enzyme'
    # PDB Preparation
    # TODO: dssp
    prepare(rec, charmm_rtf, charmm_prm, output_dir/'recprep')
    os.symlink("recprep_nmin.pdb", output_dir/"rec.pdb")
    os.symlink("recprep.psf", output_dir/"rec.psf")

    prepare(lig, charmm_rtf, charmm_prm, output_dir/'ligprep')
    os.symlink("ligprep_nmin.pdb", output_dir/"lig.pdb")
    os.symlink("ligprep.psf", output_dir/"lig.psf")

    # PIPER
    (output_dir).mkdir_p()
    piper_cmd = ['sblu', 'docking', 'piper']
    piper_cmd += ['-O', output_dir]
    piper_cmd += ['-p', atoms_prm]
    piper_cmd += ['-f', PRMS_DIR/'coeffs'/'coeffs.0.0.6.enzyme']
    piper_cmd += ['-r', rotations]
    piper_cmd += [output_dir/'rec.pdb', output_dir/'lig.pdb']
    logger.info(' '.join(piper_cmd))
    check_call(piper_cmd)

    coeffs = (0, 1, 2, 3)

    # Clustering and minimization
    for c in coeffs:
        ft_file = 'ft.{:03d}.00'.format(c)
        pwrmsd_matrix = 'clustermat.{}'.format(ft_file)
        cluster_file = 'clusters.{}.json'.format(ft_file)

        if not (output_dir/ft_file).exists():
            logging.warning('ftfile {} not found: skipping'.format(ft_file))
            continue

        pwrmsd_cmd = ['sblu', 'measure', 'pwrmsd']
        pwrmsd_cmd += ['--only-interface', '--only-CA']
        pwrmsd_cmd += ['-o', pwrmsd_matrix]
        pwrmsd_cmd += ['--rec', output_dir/'rec.pdb']
        pwrmsd_cmd += [output_dir/'lig.pdb', output_dir/ft_file, rotations]
        logger.info(' '.join(pwrmsd_cmd))
        check_call(pwrmsd_cmd)

        cluster_cmd = ['sblu', 'docking', 'cluster']
        cluster_cmd += ['-r', '9.0', '-s', '10', '-l', '30']
        cluster_cmd += ['--json', '-o', output_dir/cluster_file]
        cluster_cmd += [output_dir/pwrmsd_matrix]
        logger.info(' '.join(cluster_cmd))
        check_call(cluster_cmd)

        minimize_cmd = ['sblu', 'cluspro', 'minimize']
        minimize_cmd += ['--rtf', charmm_rtf]
        minimize_cmd += ['--prm', charmm_prm]
        minimize_cmd += ['--atoms-prm', atoms_prm]
        minimize_cmd += [output_dir/'rec.pdb', output_dir/'rec.psf']
        minimize_cmd += [output_dir/'lig.pdb', output_dir/'lig.psf']
        minimize_cmd += ['-o', output_dir/'model.{:03d}'.format(c)]
        minimize_cmd += [cluster_file, ft_file, rotations]
        logger.info(' '.join(minimize_cmd))
        check_call(minimize_cmd)


def run_other():
    raise NotImplementedError


def run_antibody():
    raise NotImplementedError


@click.command('local', short_help="Run ClusPro docking locally.")
@click.argument("rec", type=click.Path(exists=True))
@click.argument("lig", type=click.Path(exists=True))
@click.option("-o", "--output-dir", type=click.Path())
@click.option('-m', "--mode", default='enzyme',
              type=click.Choice(['enzyme', 'other', 'antibody']))
def cli(output_dir, mode,
        rec, lig):
    if output_dir is None:
        output_dir = "."
    output_dir = Path(output_dir)
    output_dir.mkdir_p()

    if mode == 'enzyme':
        run_enzyme(rec, lig,
                   PRMS_DIR/'charmm_param.rtf', PRMS_DIR/'charmm_param.prm',
                   PRMS_DIR/'rotsets'/'rot70k.mol2.prm', output_dir)
    elif mode == 'other':
        run_other()
    elif mode == 'antibody':
        run_antibody()
    else:
        logger.warning('unknown mode: {}'.format(mode))
