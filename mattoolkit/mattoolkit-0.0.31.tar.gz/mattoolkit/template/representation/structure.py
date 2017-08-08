from pymatgen.io.cif import CifParser

from .base import BaseRepresentation
from ..schema import StructureSchema
from ...api import StructureResourceItem, StructureResourceList


class StructureRepresentation(BaseRepresentation):
    """ Structure Representation

    """

    SCHEMA = StructureSchema
    RESOURCE = StructureResourceItem

    def __init__(self, document, filename, search_api=True):
        super().__init__(document, filename, search_api)
        self._structure = self._parse_structure()

    def _parse_structure(self):
        data = self.document['spec']['data']
        format = self.document['spec']['format']
        if format == 'cif':
            structure = (CifParser.from_string(data)).get_structures()[0]
        return structure

    def determine_dependencies(self, candidates):
        self._dependencies = []

    def _search_api_for_duplicates(self):
        structures = StructureResourceList()
        structures.query(name=self.name, labels=self.labels)
        if len(structures.items) > 1:
            raise ValueError('Structure duplicates are one-to-one so not possible to have many', structures.items)
        return [item.id for item in structures.items]

    def as_api_resources(self):
        return [StructureResourceItem.from_structure(name=self.name, labels=self.labels, structure=self.structure)]

    @property
    def name(self):
        return self.document['metadata']['name']

    @property
    def labels(self):
        return self.document['metadata'].get('labels')

    @property
    def structure(self):
        return self._structure

    def __repr__(self):
        return f'<{self.__class__.__name__}(filename={self.filename}, name={self.name}, labels={self.labels}>)'
