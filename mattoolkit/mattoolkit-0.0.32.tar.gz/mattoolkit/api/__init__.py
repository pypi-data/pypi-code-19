from .api import api
from .structure import StructureResourceList, StructureResourceItem
from .calculation import CalculationResourceList, CalculationResourceItem
from .cluster import (
    ClusterResourceList, ClusterResourceItem,
    ClusterJobResourceList, ClusterJobResourceItem
)
from .user import UserResourceItem, UserResourceList


resource_mapping = {
    'structures': {'list':StructureResourceList, 'item':StructureResourceItem},
    'calculations': {'list':CalculationResourceList, 'item':CalculationResourceItem},
    'clusters': {'list':ClusterResourceList, 'item': ClusterResourceItem},
    'clusterjobs': {'list':ClusterJobResourceList, 'item': ClusterJobResourceItem},
    'users': {'list': UserResourceList, 'item': UserResourceItem}
}


def resource_representation(resource, uuid=None):
    if resource not in resource_mapping:
        raise ValueError('Resource %s not available' % resource)
    if uuid:
        return resource_mapping[resource]['item'](uuid)
    return resource_mapping[resource]['list']()
