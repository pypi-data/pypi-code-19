"""
georssy.simple.simple_decoder
-----------------------------
:copyright: (c) 2017 by Sergio Ferraresi.
:license: Apache2, see LICENSE for more details.
"""

import logging
import re

from models import GeoRSSEntry

logger = logging.getLogger( __name__ )

def decode( parent_node, polygons_over_boxes = False ):
    sd = simple_decoder( parent_node = parent_node, polygons_over_boxes = polygons_over_boxes )

    return GeoRSSEntry( sd.point_list, sd.line_list, sd.polygon_list, sd.feature_type_list, sd.feature_name_list, sd.relationship_list, sd.elevation_list, sd.floor_list, sd.radius_list, polygons_over_boxes = polygons_over_boxes )

class simple_decoder( object ):
    '''
    GeoRss Parser.
    GeoRSS-Simple is meant as a very lightweight format that developers and users can quickly and easily add to their existing feeds with little effort. It supports basic geometries (point, line, box, polygon) and covers the typical use cases when encoding locations.
    GeoRSS GML is a formal GML Application Profile, and supports a greater range of features, notably coordinate reference systems other than WGS-84 latitude/longitude.

    Some publishers and users may prefer to separate lat/long pairs by a comma rather than whitespace. This is permissible in Simple; GeoRSS parsers should just treat commas as whitespace.

    See http://www.georss.org/ for more information.
    '''

    def __init__( self, parent_node, polygons_over_boxes = False ):
        '''
        Constructor
        '''

        self.parent_node = parent_node
        self.p_over_b = polygons_over_boxes

        self.point_list = []
        self.line_list = []
        self.polygon_list = []
        self.feature_type_list = []
        self.feature_name_list = []
        self.relationship_list = []
        self.elevation_list = []
        self.floor_list = []
        self.radius_list = []

        self.__georss_simple()

        # Common
        self.__feature_types()
        self.__feature_name()
        self.__relationships()
        self.__elevations()
        self.__floors()
        self.__radiuses()

    def __georss_simple( self ):
        self.__simple_points()
        self.__simple_lines()
        if self.p_over_b:
            self.__simple_polygon()
        else:
            self.__simple_polygon()
            self.__simple_box()
        # TODO CIRCLE

    def __simple_points( self ):
        '''
        Example: <georss:point>45.256 -71.92</georss:point>
        '''

        point_list = self.parent_node.findall( '{http://www.georss.org/georss}point' )
        if point_list:
            logger.debug( '  "Simple Point" detected! Decoding...' )
            for point in point_list:
                tmp = re.sub( '\s+', ' ', point.text.strip().replace( ',', ' ' ) ).split()
                self.point_list.append( {
                    'type': 'POINT',
                    'mode': 'latlon',
                    'coordinates': [ float( tmp[ 0 ] ), float( tmp[ 1 ] ) ],
                    'raw': 'POINT(%s %s)' % ( str( float( tmp[ 1 ] ) ), str( float( tmp[ 0 ] ) ) ),
                } )
            return True

        logger.debug( '  No "Simple Point" detected! Nothing to decode.' )
        return False

    def __simple_lines( self ):
        '''
        Example: <georss:line>45.256 -110.45 46.46 -109.48 43.84 -109.86</georss:line>
        '''

        line_list = self.parent_node.findall( '{http://www.georss.org/georss}line' )
        if line_list:
            logger.debug( '  "Simple Line" detected! Decoding...' )
            for line in line_list:
                tmp = re.sub( '\s+', ' ', line.text.strip().replace( ',', ' ' ) ).split()
                # Gel all Latitudes
                lat_list = tmp[ 0 : len( tmp ) : 2 ]
                # Gel all Longitudes
                lon_list = tmp[ 1 : len( tmp ) : 2 ]

                line_tmp = []
                line_raw = ''
                for lat, lon in zip( lat_list, lon_list ):
                    line_tmp.append( [ float( lat ), float( lon ) ] )
                    line_raw += '%s %s,' % ( str( float( lon ) ), str( float( lat ) ) )

                self.line_list.append( {
                    'type': 'LINESTRING',
                    'mode': 'latlon',
                    'coordinates': line_tmp,
                    'raw': 'LINESTRING(%s)' % line_raw[ 0 : -1 ], # remove last comma
                } )
            return True

        logger.debug( '  No "Simple Line" detected! Nothing to decode.' )
        return False

    def __simple_polygon( self ):
        '''
        Example: <georss:polygon>45.256 -110.45 46.46 -109.48 43.84 -109.86 45.256 -110.45</georss:polygon>
        '''

        polygon_list = self.parent_node.findall( '{http://www.georss.org/georss}polygon' )
        if polygon_list:
            logger.debug( '  "Simple Polygon" detected! Decoding...' )
            for polygon in polygon_list:
                tmp = re.sub( '\s+', ' ', polygon.text.strip().replace( ',', ' ' ) ).split()
                # Gel all Latitudes
                lat_list = tmp[ 0 : len( tmp ) : 2 ]
                # Gel all Longitudes
                lon_list = tmp[ 1 : len( tmp ) : 2 ]

                polygon_tmp = []
                polygon_raw = '('
                for lat, lon in zip( lat_list, lon_list ):
                    polygon_tmp.append( [ float( lat ), float( lon ) ] )
                    polygon_raw += '%s %s,' % ( str( float( lon ) ), str( float( lat ) ) )
                # remove last comma
                polygon_raw = polygon_raw[ 0 : -1 ] + ')'

                self.polygon_list.append( {
                    'type': 'POLYGON',
                    'mode': 'latlon',
                    'coordinates': [ polygon_tmp ],
                    'raw': 'POLYGON(%s)' % polygon_raw,
                } )
            return True

        logger.debug( '  No "Simple Polygon" detected! Nothing to decode.' )
        return False

    def __simple_box( self ):
        '''
        Example: <georss:box>42.943 -71.032 43.039 -69.856</georss:box>
        '''

        box_list = self.parent_node.findall( '{http://www.georss.org/georss}box' )
        if box_list:
            logger.debug( '  "Simple Box" detected! Decoding...' )
            for box in box_list:
                tmp = re.sub( '\s+', ' ', box.text.strip().replace( ',', ' ' ) ).split()
                lc = [ tmp[ 0 ], tmp[ 1 ] ]
                uc = [ tmp[ 2 ], tmp[ 3 ] ]

                polygon_tmp = []
                polygon_tmp.append( [ float( uc[ 0 ] ), float( uc[ 1 ] ) ] )
                polygon_tmp.append( [ float( lc[ 0 ] ), float( uc[ 1 ] ) ] )
                polygon_tmp.append( [ float( lc[ 0 ] ), float( lc[ 1 ] ) ] )
                polygon_tmp.append( [ float( uc[ 0 ] ), float( lc[ 1 ] ) ] )
                polygon_tmp.append( [ float( uc[ 0 ] ), float( uc[ 1 ] ) ] )
                raw_tmp = ''
                raw_tmp += '%s %s,' % ( str( float( uc[ 1 ] ) ), str( float( uc[ 0 ] ) ) )
                raw_tmp += '%s %s,' % ( str( float( uc[ 1 ] ) ), str( float( lc[ 0 ] ) ) )
                raw_tmp += '%s %s,' % ( str( float( lc[ 1 ] ) ), str( float( lc[ 0 ] ) ) )
                raw_tmp += '%s %s,' % ( str( float( lc[ 1 ] ) ), str( float( uc[ 0 ] ) ) )
                raw_tmp += '%s %s'  % ( str( float( uc[ 1 ] ) ), str( float( uc[ 0 ] ) ) )
                self.polygon_list.append( {
                    'type': 'POLYGON',
                    'mode': 'latlon',
                    'coordinates': [ polygon_tmp ],
                    'raw': 'POLYGON((%s))' % raw_tmp,
                } )
            return True

        logger.debug( '  No "Simple Box" detected! Nothing to decode.' )
        return False

    def __feature_types( self ):
        '''
        Example: <georss:featuretypetag>city</georss:featuretypetag>
        '''

        feature_type_list = self.parent_node.findall( '{http://www.georss.org/georss}featuretypetag' )
        if feature_type_list:
            logger.debug( '  "Feature Type" detected! Decoding...' )
            for feature_type in feature_type_list:
                tmp = feature_type.text.strip()

                self.feature_type_list.append( {
                    'type': 'FEAT_TYPE',
                    'value': tmp,
                } )
            return True

        logger.debug( '  No "Feature Type" detected! Nothing to decode.' )
        return False

    def __feature_name( self ):
        '''
        Example: <georss:featurename>Podunk</georss:featurename>
        '''

        feature_name_list = self.parent_node.findall( '{http://www.georss.org/georss}featurename' )
        if feature_name_list:
            logger.debug( '  "Feature Name" detected! Decoding...' )
            for feature_name in feature_name_list:
                tmp = feature_name.text.strip()

                self.feature_name_list.append( {
                    'type': 'FEAT_NAME',
                    'value': tmp,
                } )
            return True

        logger.debug( '  No "Feature Name" detected! Nothing to decode.' )
        return False

    def __relationships( self ):
        '''
        Example: <georss:relationshiptag>is-centered-at</georss:relationshiptag>
        '''

        relationship_list = self.parent_node.findall( '{http://www.georss.org/georss}relationshiptag' )
        if relationship_list:
            logger.debug( '  "Relationship" detected! Decoding...' )
            for relationship in relationship_list:
                tmp = relationship.text.strip()

                self.relationship_list.append( {
                    'type': 'RELAT',
                    'value': tmp,
                } )
            return True

        logger.debug( '  No "Relationship" detected! Nothing to decode.' )
        return False

    def __elevations( self ):
        '''
        Example: <georss:elev>313</georss:elev>
        '''

        elevation_list = self.parent_node.findall( '{http://www.georss.org/georss}elev' )
        if elevation_list:
            logger.debug( '  "Elevation" detected! Decoding...' )
            for elevation in elevation_list:
                tmp = elevation.text.strip()

                self.elevation_list.append( {
                    'type': 'ELEV',
                    'value': tmp,
                } )
            return True

        logger.debug( '  No "Elevation" detected! Nothing to decode.' )
        return False

    def __floors( self ):
        '''
        Example: <georss:floor>2</georss:floor>
        '''

        floor_list = self.parent_node.findall( '{http://www.georss.org/georss}floor' )
        if floor_list:
            logger.debug( '  "Floor" detected! Decoding...' )
            for floor in floor_list:
                tmp = floor.text.strip()

                self.floor_list.append( {
                    'type': 'FLOOR',
                    'value': tmp,
                } )
            return True

        logger.debug( '  No "Floor" detected! Nothing to decode.' )
        return False

    def __radiuses( self ):
        '''
        Example: <georss:radius>500</georss:radius>
        '''

        radius_list = self.parent_node.findall( '{http://www.georss.org/georss}radius' )
        if radius_list:
            logger.debug( '  "Radius" detected! Decoding...' )
            for radius in radius_list:
                tmp = radius.text.strip()

                self.radius_list.append( {
                    'type': 'RADIUS',
                    'value': tmp,
                } )
            return True

        logger.debug( '  No "Radius" detected! Nothing to decode.' )
        return False
