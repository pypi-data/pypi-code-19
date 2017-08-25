"""
georssy.api
---------------
:copyright: (c) 2017 by Sergio Ferraresi.
:license: Apache2, see LICENSE for more details.
"""
from decoder import decoder

def decode( parent_node = None, polygons_over_boxes = False ):
    d = decoder( parent_node, polygons_over_boxes )
    return d.georss_entry if d else None
