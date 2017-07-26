# coding: utf-8

from .base import BaseRepresentation
from .structure import StructureRepresentation
from .cluster import ClusterRepresentation

from ..schema import CalculationSchema
from ...api import (
    CalculationResourceItem, CalculationResourceList,
    StructureResourceList, StructureResourceItem,
    ClusterResourceList, ClusterResourceItem,
    ClusterJobResourceItem
)
from ...api.resource import ResourceItem


class CalculationRepresentation(BaseRepresentation):
    """ Calculation Representation

    """

    SCHEMA = CalculationSchema
    RESOURCE = CalculationResourceItem

    def _search_api_for_duplicates(self):
        calculations = CalculationResourceList()
        calculations.query(name=self.name, labels=self.labels)
        return [item.id for item  in calculations.items]

    def _search_api_for_structure_dependencies(self):
        selector = self.document['spec']['structure']['selector']
        type_mapping = {
            'Structure': StructureResourceList,
            'Calculation': CalculationResourceList,
        }
        resource = type_mapping[selector['type']]()
        resource.query(labels=selector['labels'])
        return resource.items

    def _search_api_for_cluster_dependencies(self):
        resources = []
        clusters = ClusterResourceList()
        clusters.get()
        for cluster in clusters.items:
            if cluster.uri == self.document['spec']['job']['cluster']:
                resources.append(cluster)
        return resources

    def as_api_resources(self):
        self.determine_dependencies() # All dependencies should be satisfied since acceced in learized manner
        for dependency in self.dependencies:
            if not isinstance(dependency, ResourceItem):
                raise TypeError('All dependencies should be satisfied by created resource thus need to be type ResourceItem')
        cluster_dependency = [d for d in self.dependencies if isinstance(d, ClusterResourceItem)][0]
        structure_dependencies = [d for d in self.dependencies if isinstance(d, (StructureResourceItem, CalculationResourceItem))]

        spec = self.document['spec']
        selector = spec['structure']['selector']
        inputs = {**spec['calculation']}
        del inputs['software']

        api_resources = []
        for structure_dependency in structure_dependencies:
            calculation_item = CalculationResourceItem(None)
            calculation_item.data = {
                'name': self.name,
                'labels': self.labels +  ['index:0'],
                'type': spec['calculation']['software'],
                'inputs': inputs,
                'initial_structure': structure_dependency.id if selector['type'] == 'Structure' else None,
                'previous_calculation': structure_dependency.id if selector['type'] == 'Calculation' else None
            }

            cluster_job_item = ClusterJobResourceItem(None)
            cluster_job_item.data = {
                'calculation': calculation_item,
                'cluster': cluster_dependency.id,
                'queue': spec['job']['queue'],
                'cores': spec['job']['cores'],
                'time': spec['job']['time']
            }
            api_resources.append((calculation_item, cluster_job_item))
        return api_resources

    def determine_dependencies(self, candidates=None):
        candidates = candidates or []

        selector = self.document['spec']['structure']['selector']
        type_mapping = {
            'Structure': StructureRepresentation,
            'Calculation': CalculationRepresentation,
            'Cluster': ClusterRepresentation
        }
        required_type = type_mapping[selector['type']]
        cluster_dependency = []
        structure_dependencies = []

        # Search cluster dependencies
        for candidate in candidates:
            if isinstance(candidate, ClusterRepresentation):
                if candidate.uri == self.document['spec']['job']['cluster']:
                    cluster_dependency.append(candidate)
            elif isinstance(candidate, required_type) and candidate is not self:
                if set(selector['labels']) <= set(candidate.labels):
                    structure_dependencies.append(candidate)

        # Always prefer api dependencies
        if self._search_api:
            dependencies = self._search_api_for_structure_dependencies()
            if dependencies:
                structure_dependencies = dependencies

            dependencies = self._search_api_for_cluster_dependencies()
            if dependencies:
                cluster_dependency = dependencies

        if len(structure_dependencies) > 1 and selector['many'] == False:
            raise ValueError('Selector found multiple dependencies but many was specified as False', structure_dependencies)

        if len(cluster_dependency) != 1:
            raise ValueError('Single cluster required for calculation only found: ', cluster_dependency)
        self._dependencies = structure_dependencies + cluster_dependency

    def inputs(self, structure_symbols):
        # kpoints: grid_density, reciprocal_density
        from pymatgen.io.vasp.sets import (
            MPRelaxSet, MPStaticSet
        )

        template_map = {
            'MPRelaxSet': MPRelaxSet,
            'MPStaticSet': MPStaticSet
        }
        user_incar_settings, user_kpoints_settings
        pass


    @property
    def name(self):
        return self.document['metadata']['name']

    @property
    def labels(self):
        return self.document['metadata'].get('labels')

    @property
    def many(self):
        return self.document['spec']['structure']['selector']['many']

    def __repr__(self):
        return f'<{self.__class__.__name__}(filename={self.filename}, name={self.name}, labels={self.labels}>'

    def __str__(self):
        labels_string = '\n'.join('│    ├── %s' % label for label in self.labels)
        duplicates_string = '\n'.join('│    ├── %s' % repr(item) for item in self.resource_items)
        dependencies_string = '\n'.join('     ├── %s' % repr(dependency) for dependency in self.dependencies)
        return f'Calculation: {self.name}\n├── labels\n{labels_string}\n├── duplicates\n{duplicates_string}\n└── dependencies\n{dependencies_string}\n'
