"""
georssy.decoder
---------------
:copyright: (c) 2017 by Sergio Ferraresi.
:license: Apache2, see LICENSE for more details.
"""

import logging
import re

from gml.gml_decoder import decode as g_decoder
from simple.simple_decoder import decode as s_decoder

logger = logging.getLogger( __name__ )

class decoder( object ):
    '''
    GeoRss Parser.
    GeoRSS-Simple is meant as a very lightweight format that developers and users can quickly and easily add to their existing feeds with little effort. It supports basic geometries (point, line, box, polygon) and covers the typical use cases when encoding locations.
    GeoRSS GML is a formal GML Application Profile, and supports a greater range of features, notably coordinate reference systems other than WGS-84 latitude/longitude.

    Some publishers and users may prefer to separate lat/long pairs by a comma rather than whitespace. This is permissible in Simple; GeoRSS parsers should just treat commas as whitespace.

    See http://www.georss.org/ for more information.
    '''

    def __init__( self, parent_node = None, polygons_over_boxes = False ):
        '''
        Constructor
        '''

        if parent_node is None:
            msg = 'GeoRSS parent node NOT valid'
            logger.error( msg )

            raise ValueError( msg )

        logger.debug( 'georssy parameters:' )
        logger.debug( '  Polygons over Boxes: "%s"' % ( 'Y' if polygons_over_boxes else 'N' ) )

        self.georss_entry = s_decoder( parent_node = parent_node, polygons_over_boxes = polygons_over_boxes )
        other = g_decoder( parent_node = parent_node, polygons_over_boxes = polygons_over_boxes )
        self.georss_entry.merge( other = other )

        logger.debug( 'georssy decoded elements:' )
        if self.georss_entry.point_list:
            logger.debug( '  Points: "%s"' % str( self.georss_entry.point_list ) )
        if self.georss_entry.line_list:
            logger.debug( '  Lines: "%s"' % str( self.georss_entry.line_list ) )
        if self.georss_entry.polygon_list:
            logger.debug( '  Polygons: "%s"' % str( self.georss_entry.polygon_list ) )
        if self.georss_entry.feature_type_list:
            logger.debug( '  Feature Types: "%s"' % str( self.georss_entry.feature_type_list ) )
        if self.georss_entry.feature_name_list:
            logger.debug( '  Feature Names: "%s"' % str( self.georss_entry.feature_name_list ) )
        if self.georss_entry.relationship_list:
            logger.debug( '  Relationships: "%s"' % str( self.georss_entry.relationship_list ) )
        if self.georss_entry.elevation_list:
            logger.debug( '  Elevations: "%s"' % str( self.georss_entry.elevation_list ) )
        if self.georss_entry.floor_list:
            logger.debug( '  Floors: "%s"' % str( self.georss_entry.floor_list ) )
