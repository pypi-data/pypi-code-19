from pymatgen import Structure, Lattice
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

from .resource import ResourceList, ResourceItem


def structure_to_schema(structure, name="Untitled PMG Structure"):
    return {
        'name': name,
        'labels': ['auto'],
        'lattice': structure.lattice.matrix.tolist(),
        'atoms': [{'symbol': atom.specie.name, 'position': atom.coords.tolist()} for atom in structure],
        'supercell': [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    }


def schema_to_structure(schema):
    lattice = Lattice(schema['lattice'])
    symbols = [atom['symbol'] for atom in schema['atoms']]
    positions = [atom['position'] for atom in schema['atoms']]
    return Structure(lattice, symbols, positions, coords_are_cartesian=True)


def analyze_structure(structure):
    spacegroup = SpacegroupAnalyzer(structure)
    return {
        'volume': structure.lattice.volume,
        'formula': structure.formula,
        'num_atoms': len(structure),
        'density': structure.density,
        'symbols': structure.symbol_set,
        'spacegroup': spacegroup.get_space_group_number(),
        'spacegroup_symbol': spacegroup.get_space_group_symbol(),
        'spacegroup_hall': spacegroup.get_hall(),
        'crystal_system': spacegroup.get_crystal_system()
    }



class StructureResourceItem(ResourceItem):
    def __init__(self, id):
        super().__init__('structures', id)

    def __repr__(self):
        if self.data:
            return f'<StructureResourceItem: id: {self.id}, name: {self.name}, labels: {self.labels}'
        else:
            return f'<{self.__class__.__name__}: id: {self.id}>'

    def __str__(self):
        return f'Structure: id: {self.id}, name: {self.name}, labels: {self.labels}\n{self.structure}'

    @classmethod
    def from_structure(cls, structure, name=None, labels=None):
        if labels is None:
            labels = []
        structure_item = cls(None)
        structure_item.data = structure_to_schema(structure, name)
        structure_item.data['labels'].extend(labels)
        return structure_item

    @property
    def name(self):
        return self.data['name']

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError('name must be a string')
        self.data['name'] = value

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
    def structure(self):
        if self.data:
            return schema_to_structure(self.data)
        return None



class StructureResourceList(ResourceList):
    ITEM = StructureResourceItem

    def __init__(self):
        super().__init__('structures')
