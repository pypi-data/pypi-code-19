# coding: utf-8

from pathlib import Path
import itertools
import logging
from collections import Counter

import yaml

from .representation import (
    StructureRepresentation, CalculationRepresentation,
    ClusterRepresentation, UserRepresentation, TransformationRepresentation
)
from ..api.resource import ResourceItem

logger = logging.getLogger(__name__)


status_map = {
    'saved': '💾',
    'waiting': '⏰',
    'submitted': '➡️',
    'running': '🖥️',
    'failed': '❌',
    'completed': '✔️'
}


def cli_format_repr(representation):
    representation_map = {
        UserRepresentation:           'User:           {representation.username:<64}',
        ClusterRepresentation:        'Cluster:        {representation.uri:<64}',
        TransformationRepresentation: 'Transformation: {representation.name:<64}',
        StructureRepresentation:      'Structure:      {representation.name:<64}',
        CalculationRepresentation:    'Calculation:    {representation.name:<64}',
    }
    return representation_map[representation.__class__].format(representation=representation)


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


def parse_yaml_files(paths, recursive, search_api=True):
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
                'User': UserRepresentation,
                'Transformation': TransformationRepresentation
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


def create_resources_from_representations(representations, test=False):
    """ Resources need to be in correct order

    """
    for i, representation in enumerate(representations):
        if isinstance(representation, UserRepresentation):
            print(f'[{i:>4}] {cli_format_repr(representation)} [ skipping      ] must create manually')
        elif representation.ids: # Has duplicates (ignore)
            print(f'[{i:>4}] {cli_format_repr(representation)} [ skipping      ] exists')
        elif test:
            print(f'[{i:>4}] {cli_format_repr(representation)} [ testing       ] would create otherwise')
        else:
            count = 0
            try:
                api_resources = representation.as_api_resources()
            except ValueError as error:
                print(f'[{i:>4}] {cli_format_repr(representation)} [ stopping      ] blocks until dependant is completed')
                exit(0)
            for api_resource in api_resources:
                if isinstance(api_resource, tuple) and representation:
                    if isinstance(representation, CalculationRepresentation):
                        calculation_item, cluster_job_item = api_resource
                        calculation_item.save()
                        cluster_job_item.data['calculation'] = calculation_item.id
                        cluster_job_item.save()
                        count += 1
                    else:
                        raise ValueError('unsure of how to handle')
                else:
                    count += 1
                    api_resource.save()
            print(f'[{i:>4}] {cli_format_repr(representation)} [{count:>3} - creating ]')


def delete_resources_from_representations(representations, test=False):
    print('Deletion must be done in inverse order of dependencies')
    for i, representation in zip(range(len(representations)-1, -1, -1) , reversed(representations)):
        if isinstance(representation, (StructureRepresentation, TransformationRepresentation, CalculationRepresentation)):
            resources = representation.resource_items
            if len(resources) == 0:
                print(f'[{i:>4}] {cli_format_repr(representation)} [ skipping ] no resources exist')
            elif test:
                print(f'[{i:>4}] {cli_format_repr(representation)} [{len(resources):>3} - testing ] would delete otherwise')
            else:
                for resource in resources:
                    resource.delete()
                print(f'[{i:>4}] {cli_format_repr(representation)} [{len(resources):>3} - deleted ]')
        else:
            print(f'[{i:>4}] {cli_format_repr(representation)} [ skipping     ] must delete manually')


def status_resources_from_representations(representations, check=False):
    print('Status: ', status_map)
    for i, representation in enumerate(representations):
        if isinstance(representation, CalculationRepresentation):
            if representation.ids:
                calculation_resources = representation.resource_items
                for calculation_resource in calculation_resources:
                    calculation_resource.get()
                    if check and calculation_resource.status in {'submitted', 'running'}:
                        calculation_resource.job_status()
                        calculation_resource.get()
                statuses = [c.status for c in calculation_resources]
                status_string = ', '.join(['%d-%s' % (c, status_map[s]) for s, c in Counter(statuses).most_common()])
                print(f'[{i:>4}] {cli_format_repr(representation)} {status_string}')
            else:
                print(f'[{i:>4}] {cli_format_repr(representation)} [ representation not on server ]')


def submit_resources_from_representations(representations, test=False):
    for i, representation in enumerate(representations):
        if isinstance(representation, CalculationRepresentation):
            if representation.ids:
                count = 0
                for calculation_resource in representation.resource_items:
                    calculation_resource.get()
                    if calculation_resource.status in {'saved', 'failed'}:
                        count += 1
                        calculation_resource.submit()
                print(f'[{i:>4}] {cli_format_repr(representation)} [{count:>3} - submitted]')
            else:
                print(f'[{i:>4}] {cli_format_repr(representation)} [ representation not on server ]')


def cancel_resources_from_representations(representations, test=False):
    for i, representation in enumerate(representations):
        if isinstance(representation, CalculationRepresentation):
            if representation.ids:
                count = 0
                for calculation_resource in representation.resource_items:
                    calculation_resource.get()
                    if calculation_resource.status in {'waiting', 'submitted', 'running'}:
                        count += 1
                        calculation_resource.cancel()
                print(f'[{i:>4}] {cli_format_repr(representation)} [{count:>3} - canceled]')
            else:
                print(f'[{i:>4}] {cli_format_repr(representation)} [ representation not on server ]')
