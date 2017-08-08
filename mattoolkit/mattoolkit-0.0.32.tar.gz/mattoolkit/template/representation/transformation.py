from .base import BaseRepresentation

from ..schema import TransformationSchema
from ...api.resource import ResourceItem
from ...api import (
    StructureResourceList, StructureResourceItem,
    CalculationResourceList, CalculationResourceItem
)
from ...jobs.transformation import apply_transformations


class TransformationRepresentation(BaseRepresentation):
    """ Transformation Representation

    """
    SCHEMA = TransformationSchema
    RESOURCE = StructureResourceItem

    def _search_api_for_duplicates(self):
        structures = StructureResourceList()
        structures.query(name=self.name, labels=self.labels)
        return [item.id for item in structures.items]

    def _search_api_for_structure_dependencies(self):
        selector = self.document['spec']['structure']['selector']
        type_mapping = {
            'Structure': StructureResourceList,
            'Calculation': CalculationResourceList,
        }
        resource = type_mapping[selector['type']]()
        resource.query(labels=selector['labels'])
        return resource.items

    def as_api_resources(self):
        self.determine_dependencies()
        dependency = self.dependencies[0]
        if not isinstance(dependency, ResourceItem):
            raise TypeError('All dependencies should be satisfied by created resource thus need to be type ResourceItem')
        if isinstance(dependency, CalculationResourceItem):
            dependency.get()
            if dependency.status != "completed":
                raise ValueError('Can only use transformation on completed calculation (becuase it needs final structure)')
            input_structure = dependency.final_structure
        else: # StructureResourceItem
            input_structure = dependency.structure

        self.structures = apply_transformations(input_structure, self.document['spec']['transformations'])
        structure_resources = []
        for i, structure in enumerate(self.structures):
            labels = self.labels + ['index:%d' % i]
            structure_resources.append(StructureResourceItem.from_structure(name=self.name, labels=labels, structure=structure))
        return structure_resources

    def determine_dependencies(self, candidates=None):
        from .structure import StructureRepresentation
        from .calculation import CalculationRepresentation

        candidates = candidates or []
        selector = self.document['spec']['structure']['selector']
        type_mapping = {
            'Structure': StructureRepresentation,
            'Calculation': CalculationRepresentation,
        }
        required_type = type_mapping[selector['type']]

        representation_dependencies = []
        for candidate in candidates:
            if isinstance(candidate, required_type) and candidate is not self:
                if set(selector['labels']) <= set(candidate.labels):
                    representation_dependencies.append(candidate)

        api_dependencies = []
        if self._search_api:
            api_dependencies = self._search_api_for_structure_dependencies()

        dependencies = representation_dependencies + api_dependencies
        if len(representation_dependencies) > 1:
            raise ValueError('Transformation requires one dependency multiple found in representation %d' % len(representation_dependencies))
        elif len(api_dependencies) > 1:
            raise ValueError('Transformation requires one dependency multiple found in api %d' % len(api_dependencies))
        elif len(dependencies) == 0:
            raise ValueError('Dependencies not found for transformation' % len(resource.items))
        self._dependencies = dependencies

    @property
    def name(self):
        return self.document['metadata']['name']

    @property
    def labels(self):
        return self.document['metadata'].get('labels')
