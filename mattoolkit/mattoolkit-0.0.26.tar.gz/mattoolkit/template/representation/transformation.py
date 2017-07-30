from .base import BaseRepresentation

from ..schema import TransformationSchema
from ...api.resource import ResourceItem
from ...api import (
    StructureResourceList, StructureResourceItem,
    CalculationResourceList, CalculationResourceItem
)

from pymatgen.transformations.site_transformations import (
    InsertSitesTransformation, ReplaceSiteSpeciesTransformation, RemoveSitesTransformation,
    TranslateSitesTransformation, PartialRemoveSitesTransformation, AddSitePropertyTransformation
)
from pymatgen.transformations.standard_transformations import (
    RotationTransformation, OxidationStateDecorationTransformation, AutoOxiStateDecorationTransformation,
    OxidationStateRemovalTransformation, SupercellTransformation, SubstitutionTransformation,
    RemoveSpeciesTransformation, PartialRemoveSpecieTransformation, OrderDisorderedStructureTransformation,
    PrimitiveCellTransformation, PerturbStructureTransformation, DeformStructureTransformation,
)
from pymatgen.transformations.defect_transformations import (
    VacancyTransformation, SubstitutionDefectTransformation, AntisiteDefectTransformation,
    InterstitialTransformation
)


class TransformationRepresentation(BaseRepresentation):
    """ Transformation Representation

    """
    SCHEMA = TransformationSchema

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

        self.structures = self.apply_transformations(input_structure)
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

        dependencies = []
        for candidate in candidates:
            if isinstance(candidate, required_type) and candidate is not self:
                if set(selector['labels']) <= set(candidate.labels):
                    dependencies.append(candidate)

        if self._search_api:
            api_dependencies = self._search_api_for_structure_dependencies()
            if api_dependencies:
                dependencies = api_dependencies

        if len(dependencies) > 1:
            raise ValueError('Transformation requires one dependency multiple found %d' % len(resource.items))
        elif len(dependencies) == 0:
            raise ValueError('Dependencies not found for transformation' % len(resource.items))
        self._dependencies = dependencies

    @property
    def name(self):
        return self.document['metadata']['name']

    @property
    def labels(self):
        return self.document['metadata'].get('labels')

    def apply_transformations(self, structure):
        transformation_map = {
            'InsertSitesTransformation': InsertSitesTransformation,
            'ReplaceSiteSpeciesTransformation': ReplaceSiteSpeciesTransformation,
            'RemoveSitesTransformation': RemoveSitesTransformation,
            'TranslateSitesTransformation': TranslateSitesTransformation,
            'PartialRemoveSitesTransformation': PartialRemoveSitesTransformation,
            'AddSitePropertyTransformation': AddSitePropertyTransformation,
            'RotationTransformation': RotationTransformation,
            'OxidationStateDecorationTransformation': OxidationStateDecorationTransformation,
            'AutoOxiStateDecorationTransformation': AutoOxiStateDecorationTransformation,
            'OxidationStateRemovalTransformation': OxidationStateRemovalTransformation,
            'SupercellTransformation': SupercellTransformation,
            'SubstitutionTransformation': SubstitutionTransformation,
            'RemoveSpeciesTransformation': RemoveSpeciesTransformation,
            'PartialRemoveSpecieTransformation': PartialRemoveSpecieTransformation,
            'OrderDisorderedStructureTransformation': OrderDisorderedStructureTransformation,
            'PrimitiveCellTransformation': PrimitiveCellTransformation,
            'PerturbStructureTransformation': PerturbStructureTransformation,
            'DeformStructureTransformation': DeformStructureTransformation,
            'VacancyTransformation': VacancyTransformation,
            'SubstitutionDefectTransformation': SubstitutionDefectTransformation,
            'AntisiteDefectTransformation': AntisiteDefectTransformation,
            'InterstitialTransformation': InterstitialTransformation
        }

        def get_ranked_list(limit):
            if limit < 0:
                ranked_list = True
            elif limit == 0:
                ranked_list = False
            else:
                ranked_list = limit
            return ranked_list

        spec = self.document['spec']
        input_structures = [structure]
        for transformation in spec['transformations']:
            output_structures = []
            t = transformation_map[transformation['type']](**transformation['arguments'])
            for s in input_structures:
                result = t.apply_transformation(s, return_ranked_list=get_ranked_list(transformation.get('limit')))
                if t.is_one_to_many:
                    for r in result:
                        output_structures.append(r['structure'])
                else:
                    output_structures.append(result['structure'])
            input_structures = output_structures
        return output_structures
