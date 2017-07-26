import tempfile

import pytest


def structure():
    from pymatgen import Structure, Lattice

    lattice = Lattice.from_parameters(4.2, 4.2, 4.2, 90, 90, 90)
    positions = [[0, 0, 0], [0.5, 0.5, 0.5]]
    elements = ['Mg', 'O']
    return Structure.from_spacegroup(225, lattice, elements, positions)


# 3 minutes on laptop (4 cores) - 5 Mb
def init_vasp_directory(run_directory):
    from pymatgen.io.vasp.sets import MPStaticSet

    input_set = MPStaticSet(structure())
    input_set.write_input(run_directory)


@pytest.mark.slowtest
@pytest.mark.vasp
def test_vasp_run():
    from mattoolkit.jobs.run import archived_run

    command = ['vasp']
    backup_file = archived_run(command,
                               scratch_directory=tempfile.gettempdir(),
                               timeout=5*60, shell=False,
                               preexec_fn=init_vasp_directory)
