import click
from prody import parsePDB

from sblu.rmsd import srmsd as srmsd_func


@click.command('srmsd', short_help="Single file RMSD.")
@click.argument("pdb_crys", type=click.Path(exists=True))
@click.argument("pdb_files", type=click.Path(exists=True), nargs=-1)
@click.option("--only-CA", is_flag=True, help="Only C-alpha atoms")
@click.option("--only-backbone", is_flag=True, help="Only backbone atoms")
@click.option("--only-interface", is_flag=True, help="Only interface atoms")
@click.option("--interface-radius", type=click.FLOAT, default=10.0)
@click.option("--rec",
              type=click.Path(exists=True),
              help="PDB to use for calculating interface")
@click.option("--oneline", is_flag=True)
def cli(pdb_crys, pdb_files, only_ca, only_backbone, only_interface,
        interface_radius, rec, oneline):
    if only_interface and rec is None:
        raise click.BadOptionUsage("--only-interface requires --rec")

    crys = parsePDB(pdb_crys)
    pdbs = (parsePDB(f) for f in pdb_files)
    rec_ag = None
    if only_interface:
        rec_ag = parsePDB(rec)

    rmsds = [str(r) for r in srmsd_func(crys, pdbs, only_ca,
                                        only_backbone, only_interface,
                                        interface_radius, rec_ag)]

    sep = "\n"
    if oneline:
        sep = ","

    print(sep.join(rmsds))
