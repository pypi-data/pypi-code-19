from pathlib import Path
import itertools
import logging

import yaml

from .representation import (
    StructureRepresentation, CalculationRepresentation,
    ClusterRepresentation, UserRepresentation
)
from ..api.resource import ResourceItem

logger = logging.getLogger(__name__)


def read_yaml_files(path):
    filepath = Path(path)
    for yaml_file in itertools.chain(filepath.glob('**/*.yaml'),
                                     filepath.glob('**/*.yml')):
        for yaml_document in yaml.load_all(yaml_file.open()):
            yield (str(yaml_file), yaml_document)


def linearize_dependencies(representations):
    # Hack to linearize resolve order
    resolve_order = []
    # All Users First
    for representation in representations:
        if isinstance(representation, UserRepresentation):
            resolve_order.append(representation)

    # All Cluster, Structure Second
    for representation in representations:
        if isinstance(representation, (StructureRepresentation, ClusterRepresentation)):
            resolve_order.append(representation)

    # Finally Add Calculation in correct order
    while len(resolve_order) < len(representations):
        resolve_order_added = []
        for representation in representations:
            if representation in resolve_order:
                continue
            dependencies_satisfied = True
            for dependency in representation.dependencies:
                if isinstance(dependency, ResourceItem):
                    continue
                elif dependency not in resolve_order:
                    dependencies_satisfied = False
            if dependencies_satisfied:
                resolve_order_added.append(representation)
        if len(resolve_order_added) == 0:
            raise ValueError('Unable to linearize dependencies curently resolved list', resolve_order)
        resolve_order.extend(resolve_order_added)
    return resolve_order


def create_resources_from_representations(representations):
    """ Resources need to be in correct order

    """
    created_representations = []

    for representation in representations:
        if isinstance(representation, UserRepresentation):
            print(f'Skipping {repr(representation)} users cannot be added to api via yaml files')
        elif representation.ids: # Has duplicates (ignore)
            print(f'Skipping {repr(representation)} since has duplicates')
        else:
            print(f'Creating {repr(representation)}')
            api_resources = representation.as_api_resources()
            for api_resource in api_resources:
                if isinstance(api_resource, tuple) and representation:
                    if isinstance(representation, CalculationRepresentation):
                        calculation_item, cluster_job_item = api_resource
                        calculation_item.save()
                        cluster_job_item.data['calculation'] = calculation_item.id
                        cluster_job_item.save()
                    else:
                        raise ValueError('unsure of how to handle')
                else:
                    api_resource.save()
            created_representations.append(representation)

def parse_yaml_files(paths, recursive, test, search_api=True):
    # TODO: listen to recursive argument
    # TODO: test make do something
    representations = []
    for path in paths:
        for filename, document in read_yaml_files(path):
            if 'kind' not in document:
                raise ValueError({
                    'filename': filename,
                    'errors': {'kind', 'must be specified'}
                })

            kinds_map = {
                'Structure': StructureRepresentation,
                'Calculation': CalculationRepresentation,
                'Cluster': ClusterRepresentation,
                'User': UserRepresentation
            }

            try:
                representation = kinds_map[document['kind']](document, filename, search_api=search_api)
                representations.append(representation)
            except ValueError as e:
                raise ValueError({'filename': filename, 'errors': e.args[0]})

    logger.info(f'{len(representations)} documents discovered in {paths}')

    for representation in representations:
        representation.determine_dependencies(representations)
    resolved_order = linearize_dependencies(representations)
    return resolved_order
