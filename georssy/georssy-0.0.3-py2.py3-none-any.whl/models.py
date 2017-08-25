"""
georssy.models
--------------
:copyright: (c) 2017 by Sergio Ferraresi.
:license: Apache2, see LICENSE for more details.
"""

class GeoRSSEntry( object ):
    """The :class:`GeoRSSEntry <GeoRSSEntry>` object, containing all the
    geometries of an entry (both 'whole rss document' in 'simple' case and
    'where' tag in GML case).
    """

    def __init__( self, point_list = [], line_list = [], polygon_list = [], feature_type_list = [], feature_name_list = [], relationship_list = [], elevation_list = [], floor_list = [], radius_list = [], polygons_over_boxes = False ):
        #: Entry Point List
        self.point_list          = point_list
        #: Entry LineString List
        self.line_list           = line_list
        #: Entry Polygon and Boxes List
        self.polygon_list        = polygon_list
        #: Entry Feature Type List
        self.feature_type_list   = feature_type_list
        #: Entry Feature Name List
        self.feature_name_list   = feature_name_list
        #: Entry Relationship List
        self.relationship_list   = relationship_list
        #: Entry Elevation List
        self.elevation_list      = elevation_list
        #: Entry Floor List
        self.floor_list          = floor_list
        #: Entry Radius List
        self.radius_list         = radius_list
        #: Overwrite Boxes with Polygons
        self.polygons_over_boxes = polygons_over_boxes

    def merge( self, other ):
        if other.point_list:
            self.point_list.extend( other.point_list )
        if other.line_list:
            self.line_list.extend( other.line_list )
        if other.polygon_list:
            self.polygon_list.extend( other.polygon_list )
        if other.feature_type_list:
            self.feature_type_list = other.feature_type_list
        if other.feature_name_list:
            self.feature_name_list = other.feature_name_list
        if other.relationship_list:
            self.relationship_list = other.relationship_list
        if other.elevation_list:
            self.elevation_list = other.elevation_list
        if other.floor_list:
            self.floor_list = other.floor_list
        if other.radius_list:
            self.radius_list = other.radius_list
