"""
georssy.api
---------------
:copyright: (c) 2017 by Sergio Ferraresi.
:license: Apache2, see LICENSE for more details.
"""
from decoder import decoder

def decode( parent_node, polygons_over_boxes ):
    return decoder( parent_node, polygons_over_boxes ).georss_entry
