from pathlib import Path

import pymatgen
from pymatgen import Structure, Lattice

from mattoolkit.template.representation import VaspInputRepresentation

lattice = Lattice.from_parameters(4.2, 4.2, 4.2, 90, 90, 90)
fractional_coords = [[0, 0, 0], [0.5, 0.5, 0.5]]
structure = Structure.from_spacegroup(225, lattice, ['Mg', 'O'], fractional_coords)

input_schema = {
    'template': 'relax',
    'incar': {
        'ENCUT': 7000
    },
    'kpoints': {
        'mode': 'grid',
        'centering': 'monkhorst',
        'grid': [7, 7, 7]
    },
    'potcar': {
        'functional': 'PBE',
        'symbols': [
            {'element': 'Mg', 'extension': 'pv'}
        ]
    }
}

def test_vasp_input():
    # Hack to redirect pseudopotentials
    pymatgen.SETTINGS['PMG_VASP_PSP_DIR'] = str(Path('./test_files/potcar/').absolute())

    representation = VaspInputRepresentation(input_schema)
    vasp_input = representation.input_set(structure)
    print(vasp_input)
