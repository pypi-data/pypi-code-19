import tempfile

import pytest


lammps_file = """
units lj
atom_style atomic
lattice fcc 0.8442
region box block 0 10 0 10 0 10
create_box 1 box
create_atoms 1 box
mass 1 1.0
velocity all create 3.0 87287
pair_style lj/cut 2.5
pair_coeff 1 1 1.0 1.0 2.5
neighbor 0.3 bin
neigh_modify every 20 delay 0 check no
fix 1 all nve
thermo 50
run 1000
"""


# 5 second - 10 Kb
def init_lammps_directory(run_directory):
    with (run_directory / 'lammps.in').open('w') as f:
        f.write(lammps_file)


@pytest.mark.slowtest
@pytest.mark.lammps
def test_lammps_run():
    from mattoolkit.jobs.run import archived_run

    command = ['lammps', '-i', 'lammps.in']
    backup_file = archived_run(command,
                               scratch_directory=tempfile.gettempdir(),
                               timeout=5*60, shell=False,
                               preexec_fn=init_lammps_directory)
