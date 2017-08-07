import os
import logging
from subprocess import run, DEVNULL

import click
from path import Path

from sblu.rmsd import calc_rmsd
from sblu.ftflex import get_segment, process_report, IGNORED_RESIDUES, FARAWAY_CUTOFFS

from prody import parsePDBStream, parsePDB

logger = logging.getLogger(__name__)
EFAC = "0.5"
HOME = Path(os.environ["HOME"])


@click.command('flex-dock', short_help="Dock with flexible sidechains")
@click.option("--charmm-rtf", type=click.Path(exists=True),
              default=HOME/"prms/charmm/charmm_param.rtf")
@click.option("--charmm-prm", type=click.Path(exists=True),
              default=HOME/"prms/charmm/charmm_param.prm")
@click.option("--atoms-param", type=click.Path(exists=True))
@click.option("-r", "--rotations", type=click.Path(exists=True))
@click.option("-t", "--ntopperrot", type=click.INT, default=1)
@click.option("--prep-rec/--no-prep-rec", default=True)
@click.option("--working-dir", default=None, type=Path)
@click.option("--rec-chain", "rec_chains", multiple=True)
@click.option("--lig-chain", "lig_chains", multiple=True)
@click.option("--rec-psf", default=None, type=click.Path(exists=True))
@click.option("--rotamer-library", default=HOME/".rotamers")
@click.argument("rec_path", type=click.Path(exists=True))
@click.argument("lig_path", type=click.Path(exists=True))
@click.argument("pocket-residues")
def cli(charmm_rtf, charmm_prm,
        atoms_param, rotations,
        ntopperrot, prep_rec, working_dir,
        rec_chains, lig_chains,
        rotamer_library,
        rec_path, rec_psf, lig_path, pocket_residues):
    rec_path = Path(rec_path).abspath()
    rec_psf = Path(rec_psf).abspath()
    lig_path = Path(lig_path).abspath()
    current_directory = Path(".").abspath()
    atoms_param = Path(atoms_param).abspath()

    if working_dir is None:
        working_dir = Path(".")

    working_dir = working_dir.abspath()
    working_dir.mkdir_p()

    if prep_rec:
        cmd = ['sblu', 'pdb', 'prep']
        for chain in rec_chains:
            cmd += ['--chain', chain]
        cmd += ['--out-prefix', working_dir/"rec", rec_path]
        logger.info(" ".join(cmd))
        run(cmd)
        rec_psf = (working_dir/"rec.psf").abspath()
        rec_path = (working_dir/"rec_nmin.pdb").abspath()
    else:
        pass

    cmd = ['1sidehphobe_markms', rec_path, working_dir/"rec_nmin.ms", atoms_param]
    run(cmd, stderr=DEVNULL, check=True)

    if rec_psf is None:
        click.fail("receptor PSF required")

    logger.info(rec_path)
    with open(rec_path, "r") as f:
        rec = parsePDBStream(f)

    pocket = []
    with open(pocket_residues, "r") as f:
        for l in f:
            try:
                chain, resnum = l.strip().split()
                residue = rec.select("chain {} and resnum {}".format(chain, resnum))
                if residue is not None:
                    resnames = set(residue.getResnames())
                    if len(resnames) != 1:
                        raise Exception("multiple residue names for {}{}".format(chain, resnum))
                    resname = resnames.pop()
                    pocket.append((chain, resnum, resname))
                    logger.info("chain, residue: {}{} {}".format(chain, resnum, resname))
                else:
                    logger.error("chain, residue: {}{} not found in receptor".format(chain, resnum))
            except Exception as e:
                logger.error("Could not read chain/residue from flexible residue file")
                logger.error("Line: {}".format(l))
                raise

    sidechain_library_dir = (working_dir/"sidechains").mkdir_p()
    sidechain_list = (working_dir/"sc.list")
    movable_sidechains = False
    with open(sidechain_list, "w") as sc_list_file:
        for chain, resnum, residue_name in pocket:
            if residue_name in IGNORED_RESIDUES:
                logger.info("Skipping residue {}{} ({})".format(chain, resnum, residue_name))
                continue

            sidechain = rec.select("chain {} and resnum {}".format(chain, resnum)).copy()
            sidechain_dir = sidechain_library_dir/("{}{}".format(chain, resnum))
            cutoff = FARAWAY_CUTOFFS[residue_name]

            sidechain_dir.mkdir_p()
            sidechain_dir.chdir()

            segment = get_segment(chain, resnum, rec_path)

            cmd = ['rotamer_min',
                   "-i", "-c", "-r", "1", "-e", "-f", "-d", rotamer_library,
                   rec_psf, charmm_prm, charmm_rtf, rec_path, segment, resnum, EFAC]

            logger.info(" ".join(cmd))
            with open("report", "wb") as f:
                run(cmd, stdout=f, stderr=DEVNULL, check=True)

            all_rotamers, low_energy_rotamers = process_report("report")

            faraway_rotamers = set()
            for i in all_rotamers:
                rotamer = parsePDB("subcluster.{:03d}.pdb".format(int(i)))
                assert len(rotamer) == len(sidechain)
                rot_rmsd = calc_rmsd(rotamer, sidechain)
                logger.info("{} {} {} {}/{}".format(chain, resnum, i, rot_rmsd, cutoff))
                if rot_rmsd > cutoff:
                    faraway_rotamers.add(i)

            if faraway_rotamers & low_energy_rotamers:
                movable_sidechains = True
                sc_list_file.write("{} {}\n".format(chain, resnum))
                with open(sidechain_library_dir/"{}{}.pdb".format(chain, resnum), "w") as f:
                    for i, rotind in enumerate(sorted(faraway_rotamers & low_energy_rotamers)):
                        with open("subcluster.{:03d}.pdb".format(int(rotind))) as f2:
                            f.write("MODEL {}\n".format(i))
                            f.write(f2.read())
                            f.write("ENDMDL\n")

                cmd = ['1sidehphobe_markms_sidechain', "--chain", chain, "--resseq", resnum,
                       rec_path,
                       sidechain_library_dir/"{}{}.pdb".format(chain, resnum),
                       sidechain_library_dir/"{}{}.ms".format(chain, resnum),
                       atoms_param]
                logger.info(" ".join(cmd))
                run(cmd)

            current_directory.chdir()

    if not movable_sidechains:
        click.fail("No movable sidechains")
