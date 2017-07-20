from pymatgen.io.vasp.inputs import Poscar, Kpoints, Potcar, Incar, VaspInput
from pymatgen.io.vasp.sets import (
    MPRelaxSet, MPStaticSet, MPNonSCFSet
)
from pymatgen.symmetry.bandstructure import HighSymmKpath

from ...schema import VaspInputSchema


class VaspInputRepresentation:
    def __init__(self, document):
        document, errors = VaspInputSchema().load(document)
        if errors:
            raise ValueError(errors)
        self.document = document

    def input_set(self, structure):
        vasp_templates = {
            'relax': MPRelaxSet,
            'static': MPStaticSet,
            'nonscf': MPNonSCFSet
        }

        kpoints, user_kpoints_settings = self.kpoints_from_schema(structure)
        user_incar_settings = self.document.get('incar', {})

        if 'template' in self.document and self.document['template'] != 'none':
            base_input = vasp_templates[self.document['template']](
                structure,
                user_incar_settings=user_incar_settings,
                user_kpoints_settings=user_kpoints_settings).all_input
            if kpoints: # override template kpoints if specified
                base_input['KPOINTS'] = kpoints
        else:
            poscar = Poscar(structure)
            base_input = {
                'POSCAR': poscar,
                'INCAR': Incar(user_incar_settings),
                'POTCAR': Potcar(poscar.site_symbols),
                'KPOINTS': kpoints
            }

        potcar = self.document.get('potcar')
        functional = potcar.get('functional', 'PBE') if potcar else 'PBE'
        update_symbols = {s['element']: s['extension'] for s in potcar.get('symbols', [])}if potcar else {}
        potcar_symbols = []
        for symbol in base_input['POTCAR'].symbols:
            element = symbol.split('_', maxsplit=1)[0]
            if element in update_symbols:
                extension = update_symbols[element]
                if extension:
                    potcar_symbols.append(element + '_' + update_symbols[element])
                else:
                    potcar_symbols.append(element)
            else:
                potcar_symbols.append(symbol)
        base_input['POTCAR'] = Potcar(potcar_symbols, functional)
        return VaspInput(
            incar=base_input['INCAR'],
            poscar=base_input['POSCAR'],
            potcar=base_input['POTCAR'],
            kpoints=base_input['KPOINTS']
        )

    def kpoints_from_schema(self, structure):
        kpoints_schema = self.document.get('kpoints')
        if kpoints_schema is None:
            return None, None

        mode = kpoints_schema['mode']
        kpoints = None
        user_kpoints_settings = None
        if mode == 'grid':
            centering = kpoints_schema['centering']
            grid = kpoints_schema['grid']
            offset = kpoints_schema.get('offset', [0, 0, 0])
            if centering == 'gamma':
                kpoints =  Kpoints.gamma_automatic(grid, offset)
            elif centering == 'monkhorst':
                kpoints =  Kpoints.monkhorst_automatic(grid, offset)
        elif mode == 'line':
            kpoint_coords = []
            kpoint_labels = []

            for path in kpoints_config['paths']:
                kpoint_coords.append(path[0]['kpoint'])
                kpoint_labels.append(path[0]['label'])
                for i in range(1, len(path) - 1):
                    kpoint_coords.append(path[i]['kpoint'])
                    kpoint_labels.append(path[i]['label'])
                    kpoint_coords.append(path[i]['kpoint'])
                    kpoint_labels.append(path[i]['label'])
                kpoint_coords.append(path[-1]['kpoint'])
                kpoint_labels.append(path[-1]['label'])

            kpoints = Kpoints(**{
                'comment': 'User Kpoint Line',
                'num_kpts': int(kpoints_config['divisions']),
                'style': Kpoints.supported_modes.Line_mode,
                'coord_type': 'Reciprocal',
                'kpts': kpoints,
                'kpts_weights': [1.0 for _ in range(len(kpoints))],
                'labels': labels
            })
        elif mode == 'automatic':
            if 'line_density' in kpoints_schema:
                kpoints_line_density = kpoints_schema['line_density']
                kpath = HighSymmKpath(self.structure)
                frac_k_points, k_points_labels = kpath.get_kpoints(
                    line_density=kpoints_line_density,
                    coords_are_cartesian=False)
                kpoints = Kpoints(
                    comment="Non SCF run along symmetry lines",
                    style=Kpoints.supported_modes.Reciprocal,
                    num_kpts=len(frac_k_points),
                    kpts=frac_k_points, labels=k_points_labels,
                    kpts_weights=[1] * len(frac_k_points))
            else:
                user_kpoints_settings = {**kpoints_schema}
                del user_kpoints_settings['mode']
        return kpoints, user_kpoints_settings
