import os

from pymatgen.io.vasp.inputs import Incar, Poscar, Kpoints, Potcar, VaspInput
from pymatgen import Structure
from pymatgen.electronic_structure.bandstructure import BandStructure, BandStructureSymmLine
from pymatgen.electronic_structure.core import Spin
import numpy as np

from .resource import ResourceList, ResourceItem
from .structure import StructureResourceItem
from .cluster import ClusterJobResourceItem
from .api import MTKAPIError


class VaspCalculationResourceItem(ResourceItem):
    def __init__(self, id):
        super().__init__('calculations/vasp', id)

    @property
    def calculation(self):
        calculation_rec = CalculationResourceItem(self.data['calculation'])
        calculation_rec.get()
        return calculation_rec

    @property
    def initial_structure(self):
        return Structure.from_dict(self.vasprun['input']['crystal'])

    @property
    def final_structure(self):
        return Structure.from_dict(self.vasprun['output']['crystal'])

    @property
    def outcar(self):
        return self.data['outcar']

    @property
    def vasprun(self):
        return self.data['vasprun']

    @property
    def converged(self):
        return self.vasprun['has_vasp_completed']

    @property
    def bandgap(self):
        return self.vasprun['output']['bandgap']

    @property
    def fermi_energy(self):
        return self.vasprun['output']['efermi']

    @property
    def final_energy(self):
        return self.vasprun['output']['final_energy']

    @property
    def final_forces(self):
        return self.vasprun['output']['ionic_steps'][-1]['forces']

    @property
    def final_stress(self):
        return self.vasprun['output']['ionic_steps'][-1]['stress']

    @property
    def eigenvalues(self):
        return self.vasprun['output']['eigenvalues']

    @property
    def ionic_steps(self):
        return self.vasprun['output']['ionic_steps']

    @property
    def bandstructure(self):
        # Include Projections as well later
        actual_kpoints = self.vasprun['input']['kpoints']['actual_points']
        kpoints = [kpoint['abc'] for kpoint in actual_kpoints]
        lattice_rec = self.final_structure.lattice.reciprocal_lattice
        structure = self.final_structure
        efermi = self.fermi_energy
        eigenvals = {}

        spin_value = {
            '1': Spin.up,
            '-1': Spin.down
        }

        for spin, v in self.eigenvalues.items():
            v = np.swapaxes(v, 0, 1)
            eigenvals[spin_value[spin]] = v[:, :, 0]

        if self.vasprun['input']['kpoints']['generation_style'] == 'Line_mode':
            kpoint_labels = {}
            for path in self.calculation.data['inputs']['kpoints']['paths']:
                for kpoint in path:
                    kpoint_labels[kpoint['label']] = kpoint['kpoint']
            return BandStructureSymmLine(kpoints, eigenvals,
                                         self.final_structure.lattice.reciprocal_lattice,
                                         self.fermi_energy,
                                         kpoint_labels,
                                         structure=self.final_structure)
        return BandStructure(kpoints, eigenvals,
                             self.final_structure.lattice.reciprocal_lattice,
                             self.fermi_energy,
                             structure=self.final_structure)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.data)


def to_kpoints_schema(kpoints):
    if kpoints.style == Kpoints.supported_modes.Gamma:
        return {
            'mode': 'grid',
            'centering': 'gamma',
            'grid': kpoints.kpts[0],
            'offset': kpoints.kpts_shift
        }
    elif kpoints.style == Kpoints.supported_modes.Monkhorst:
        return {
            'mode': 'grid',
            'centering': 'monkhorst',
            'grid': kpoints.kpts[0],
            'offset': kpoints.kpts_shift
        }
    else:
        raise ValueError('Currently no support for mode {}'.format(kpoints.style))


def to_potcar_schema(potcar):
    symbols = []
    for symbol in potcar.symbols:
        if '_' in symbol:
            element, extension = symbol.split('_', 1)
        else:
            element, extension = symbol, ''
        symbols.append({'element': element, 'extension': extension})
    return {
        'functional': potcar.functional,
        'symbols': symbols
    }


class CalculationResourceItem(ResourceItem):
    SUPPORTED_FORMATS = ['VASP']

    def __init__(self, id):
        super().__init__('calculations/general', id)

    @property
    def name(self):
        return self.data['name']

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError('name must be a string')
        self.data['name'] = value

    @property
    def status(self):
        return self.data['status']

    @property
    def format(self):
        return self.data['type']

    @format.setter
    def format(self, value):
        if value not in self.SUPPORTED_FORMATS:
            error = 'format {} not in supported formats for calculations: {}'
            raise ValueError(error.format(value, self.SUPPORTED_FORMATS))
        self.data['type'] = value

    @property
    def labels(self):
        return self.data['labels']

    @labels.setter
    def labels(self, value):
        if not isinstance(value, list):
            raise ValueError('labels must be list')

        for label in value:
            if not isinstance(label, str):
                raise ValueError('each element in labels must be string')
        self.data['labels'] = value

    @property
    def initial_structure(self):
        initial_structure_id = self.data.get('initial_structure')
        if initial_structure_id:
            structure_rec = StructureResourceItem(initial_structure_id)
            structure_rec.get()
            return structure_rec.structure
        elif initial_structure_id is None and self.data.get('previous_calculation'):
            # attempt to get initial structure from previous_calculation
            calculation_rec = CalculationResourceItem(self.data['previous_calculation'])
            calculation_rec.get()
            if calculation_rec.status == 'completed':
                return calculation_rec.final_structure
            else:
                raise ValueError('previous calculation not complete cannot get initial structure')
        else:
            raise ValueError('Improperly configured calculation_item')


    @property
    def final_structure(self):
        if self.data['status'] not in ['completed']:
            raise ValueError('Calculation must be complete for final structure')

        structure_rec = StructureResourceItem(self.data['final_structure'])
        structure_rec.get()
        return structure_rec.structure

    @property
    def previous_calculation(self):
        if self.data.get('previous_calculation') is None:
            return None

        calculation_rec = CalculationResourceItem(self.data['previous_calculation'])
        calculation_rec.get()

        # TODO: maybe should not throw error but to be safe
        if calculation_rec.data['status'] not in ['failed', 'completed']:
            raise ValueError('Calculation must be complete or failed for previous calculation')
        return calculation_rec

    @property
    def cluster_job(self):
        if self.data.get('cluster_job') is None:
            return None

        cluster_job_rec = ClusterJobResourceItem(self.data['cluster_job'])
        cluster_job_rec.get()
        return cluster_job_rec


    @property
    def input(self):
        if self.format == 'VASP':
            from ..template.representation import VaspInputRepresentation

            representation = VaspInputRepresentation(self.data['inputs'])
            return representation.input_set(self.initial_structure)
        else:
            raise ValueError('Can only handle VASP calculation inputs')


    @classmethod
    def from_structure(cls, structure, calculation_input, name=None, labels=None):
        if not isinstance(structure, StructureResourceItem) or structure.id == None:
            raise ValueError('structure must be of type StructureResourceItem and have id')
        calculation_rec = CalculationResourceItem(None)
        calculation_rec.data = {
            'initial_structure': structure.id
        }
        return cls._from_constructor_handler(calculation_rec, calculation_input, name, labels)

    @classmethod
    def from_previous_calculation(cls, calculation, calculation_input, name=None, labels=None):
        if not isinstance(calculation, CalculationResourceItem) or calculation.id == None:
            raise ValueError('calculation must be of type CalculationResourceItem and have id')

        calculation_rec = CalculationResourceItem(None)
        calculation_rec.data = {
            'previous_calculation': calculation.id,
            'initial_structure': calculation.data.get('final_structure')
        }
        return cls._from_constructor_handler(calculation_rec, calculation_input, name, labels)


    @classmethod
    def _from_constructor_handler(cls, calculation_rec, calculation_input, name, labels):
        calculation_rec.data.update({
            'name': name or 'mattoolkit api',
            'labels': ['auto'] + labels,
        })

        if isinstance(calculation_input, VaspInput):
            calculation_rec.data.update({
                'type': 'VASP',
                'inputs': {
                    'incar': calculation_input['INCAR'].get_string(),
                    'kpoints': to_kpoints_schema(calculation_input['KPOINTS']),
                    'potcar': to_potcar_schema(calculation_input['POTCAR'])
                }
            })
            return calculation_rec
        else:
            raise ValueError('Calculations can only be made from VaspInput, currently')

    @property
    def results(self):
        if self.format == 'VASP':
            vasp_rec = VaspCalculationResourceItem(self.data['vasp_calculation'])
            vasp_rec.get()
            return vasp_rec
        else:
            raise ValueError('Can only handle VASP calculation results')

    def submit(self):
        if self.data['cluster_job'] is None:
            raise ValueError('Can only submit job if it has a cluster_job associated')

        response = self.api.session.post(self.url + '/' + str(self.id), json={'action': 'submit'})
        if response.status_code != 200:
            raise ValueError(response.text)
        self.get()

    def cancel(self):
        if self.status not in ['waiting', 'submitted', 'running']:
            raise ValueError('cannot get status of non-running or non-submitted jobs')
        data = {'action': 'cancel'}
        response = self.api.session.post(self.url + '/' + str(self.id), json=data)
        if response.status_code != 200:
            raise ValueError(response.text)
        self.get()
        return response.json()

    def job_status(self):
        if self.status not in ['submitted', 'running']:
            raise ValueError('cannot get status of non-running or non-submitted jobs')
        data = {'action': 'status'}
        response = self.api.session.post(self.url + '/' + str(self.id), json=data)
        if response.status_code != 200:
            raise ValueError(response.text)
        self.get()
        return response.json()

    def notify_running(self, directory):
        data = {'directory': str(directory.absolute()), 'action': 'running'}
        response = self.api.session.post(self.url + '/' + str(self.id), json=data)
        if response.status_code != 200:
            raise ValueError(response.text)

    def download_results(self, directory):
        if self.data['status'] not in ['completed', 'failed']:
            raise ValueError('Only completed or failed vasp calculations can be downloaded')

        if self.format == 'VASP':
            url = self.api.API_ROOT + '/calculations/vasp/{}/download'.format(self.data['vasp_calculation'])
            response = self.api.session.get(url)
            if response.status_code != 200:
                raise MTKAPIError(response.status_code, response.text)
            filepath = os.path.join(directory, 'vasp_result.zip')
            with open(filepath, 'wb') as f:
                f.write(response.content)
        else:
            raise NotImplementedError('Only VASP calulcations can be uploaded at the moment')
        return filepath

    def upload_results(self, filename):
        if self.format == 'VASP':
            with open(filename, 'rb') as f:
                url = self.api.API_ROOT + '/calculations/vasp'
                files = {
                    'file': ('vasp.zip', f, 'application/zip'),
                }
                data = {
                    'calculation': str(self.id)
                }
                response = self.api.session.post(url, files=files, data=data)
                if response.status_code != 200:
                    raise MTKAPIError(response.status_code, response.text)
            print('Calculation Uploaded Successfully')
        else:
            raise NotImplementedError('Only VASP calulcations can be uploaded at the moment')

    def __repr__(self):
        if self.data:
            return f'<{self.__class__.__name__}: id: {self.id}, name: {self.name}, labels: {self.labels}>'
        else:
            return f'<{self.__class__.__name__}: id: {self.id}>'


class CalculationResourceList(ResourceList):
    ITEM = CalculationResourceItem

    def __init__(self):
        super().__init__('calculations/general')
