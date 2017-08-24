"""
georssy.gml.gml_decoder
-----------------------
:copyright: (c) 2017 by Sergio Ferraresi.
:license: Apache2, see LICENSE for more details.
"""

import logging
import re

from ..models import GeoRSSEntry

logger = logging.getLogger( __name__ )

def decode( parent_node, polygons_over_boxes = False ):
    gd = gml_decoder( parent_node = parent_node, polygons_over_boxes = polygons_over_boxes )

    return GeoRSSEntry( point_list = gd.point_list, line_list = gd.line_list, polygon_list = gd.polygon_list )

class gml_decoder( object ):
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
        self.where_node = None

        self.point_list = []
        self.line_list = []
        self.polygon_list = []

        self.__georss_gml()

    def __georss_gml( self ):
        '''
        Example:
        <georss:where>
            <gml:Point>
                <gml:pos>45.256 -71.92</gml:pos>
            </gml:Point>
        </georss:where>
        '''

        self.where_node = self.parent_node.find( '{http://www.georss.org/georss}where' )

        if self.where_node is not None:
            self.__gml_points()
            self.__gml_lines()
            if self.p_over_b:
                self.__gml_polygons()
            else:
                self.__gml_polygons()
                self.__gml_boxes()

    def __gml_points( self ):
        '''
        Example:
            <gml:Point>
                <gml:pos>45.256 -71.92</gml:pos>
            </gml:Point>

        The following are DEPRECATED:
            <gml:Point>
                <gml:coordinates>...</gml:coordinates>
            </gml:Point>

            <gml:Point>
                <gml:coord>...</gml:coord>
            </gml:Point>
        '''

        point_list = self.where_node.findall( '{http://www.opengis.net/gml}Point' )
        if point_list:
            logger.debug( '  "GML Point" detected! Decoding...' )
            for point in point_list:
                pos_list = point.findall( '{http://www.opengis.net/gml}pos' )

                for pos in pos_list:
                    tmp = re.sub( '\s+', ' ', pos.text.strip().replace( ',', ' ' ) ).split()
                    self.point_list.append( {
                        'type': 'POINT',
                        'mode': 'latlon',
                        'coordinates': [ float( tmp[ 0 ] ), float( tmp[ 1 ] ) ],
                        'raw': 'POINT(%s %s)' % ( str( float( tmp[ 1 ] ) ), str( float( tmp[ 0 ] ) ) ),
                    } )
                return True

            logger.debug( '  No "GML Point" detected! Nothing to decode.' )
            return False

    def __gml_lines( self ):
        '''
        Example:
            <gml:LineString>
                <gml:posList>45.256 -110.45 46.46 -109.48 43.84 -109.86</gml:posList>
            </gml:LineString>
        or:
            <gml:LineString>
                <gml:pos>45.256 -110.45</gml:pos>
                <gml:pos>46.46 -109.48</gml:pos>
                <gml:pos>43.84 -109.86</gml:pos>
            </gml:LineString>
        or:
            <gml:LineString>
                <gml:pointProperty>
                    <gml:Point>
                        <gml:pos>45.256 -110.45</gml:pos>
                    </gml:Point>
                    <gml:Point>
                        <gml:pos>46.46 -109.48</gml:pos>
                    </gml:Point>
                    <gml:Point>
                        <gml:pos>43.84 -109.86</gml:pos>
                    </gml:Point>
                </gml:pointProperty>
            </gml:LineString>

        The following are DEPRECATED:
            <gml:LineString>
                <gml:coordinates>...</gml:coordinates>
            </gml:LineString>

            <gml:LineString>
                <gml:coord>...</gml:coord>
                ...
            </gml:LineString>

            <gml:LineString>
                <gml:pointRep>...</gml:pointRep>
            </gml:LineString>
        '''

        line_list = self.where_node.findall( '{http://www.opengis.net/gml}LineString' )
        if line_list:
            logger.debug( '  "GML Line" detected! Decoding...' )
            for line in line_list:
                poslist = line.find( '{http://www.opengis.net/gml}posList' )
                # get all pos nodes, if existing
                pos_list = line.findall( './/{http://www.opengis.net/gml}pos' )

                if poslist:
                    tmp = re.sub( '\s+', ' ', poslist.text.strip().replace( ',', ' ' ) ).split()
                    # Gel all Latitudes
                    lat_list = tmp[ 0 : len( tmp ) : 2 ]
                    # Gel all Longitudes
                    lon_list = tmp[ 1 : len( tmp ) : 2 ]

                    line_tmp = []
                    line_raw = ''
                    for lat, lon in zip( lat_list, lon_list ):
                        line_tmp.append( [ float( lat ), float( lon ) ] )
                        line_raw += '%s %s,' % ( str( float( lon ) ), str( float( lat ) ) )
                    # remove last comma
                    line_raw = line_raw[ 0 : -1 ]

                    self.line_list.append( {
                        'type': 'LINESTRING',
                        'coordinates': line_tmp,
                        'raw': 'LINESTRING(%s)' % line_raw,
                    } )
                elif pos_list and len( pos_list ) > 0:
                    line_tmp = []
                    line_raw = ''
                    for pos in pos_list:
                        tmp = re.sub( '\s+', ' ', pos.text.strip().replace( ',', ' ' ) ).split()
                        line_tmp.append( [ float( tmp[ 0 ] ), float( tmp[ 1 ] ) ] )
                        line_raw += '%s %s,' % ( str( float( tmp[ 1 ] ) ), str( float( tmp[ 0 ] ) ) )
                    # remove last comma
                    line_raw = line_raw[ 0 : -1 ]

                    self.line_list.append( {
                        'type': 'LINESTRING',
                        'mode': 'latlon',
                        'coordinates': line_tmp,
                        'raw': 'LINESTRING(%s)' % line_raw,
                    } )
                return True

            logger.debug( '  No "GML Line" detected! Nothing to decode.' )
            return False

    def __gml_polygons( self ):
        '''
        Example:
            <gml:Polygon>
                <gml:exterior>
                    <gml:LinearRing>
                        <gml:posList>45.256 -110.45 46.46 -109.48 43.84 -109.86 45.256 -110.45</gml:posList>
                    </gml:LinearRing>
                </gml:exterior>
            </gml:Polygon>
        or:
            <gml:Polygon>
                <gml:exterior>
                    <gml:LinearRing>
                        <gml:pos>45.256 -110.45</gml:pos>
                        <gml:pos>46.46 -109.48</gml:pos>
                        <gml:pos>43.84 -109.86</gml:pos>
                        <gml:pos>45.256 -110.45</gml:pos>
                    </gml:LinearRing>
                </gml:exterior>
            </gml:Polygon>
        or:
            <gml:Polygon>
                <gml:exterior>
                    <gml:LinearRing>
                        <gml:pointProperty>
                            <gml:Point>
                                <gml:pos>45.256 -110.45</gml:pos>
                            </gml:Point>
                            <gml:Point>
                                <gml:pos>46.46 -109.48</gml:pos>
                            </gml:Point>
                            <gml:Point>
                                <gml:pos>43.84 -109.86</gml:pos>
                            </gml:Point>
                            <gml:Point>
                                <gml:pos>45.256 -110.45</gml:pos>
                            </gml:Point>
                        </gml:pointProperty>
                    </gml:LinearRing>
                </gml:exterior>
            </gml:Polygon>

        The following are DEPRECATED:
            <gml:Polygon>
                <gml:exterior>
                    <gml:LinearRing>
                        <gml:coordinates>...</gml:coordinates>
                    </gml:LinearRing>
                </gml:exterior>
            </gml:Polygon>

            <gml:Polygon>
                <gml:exterior>
                    <gml:LinearRing>
                        <gml:coord>...</gml:coord>
                    </gml:LinearRing>
                </gml:exterior>
            </gml:Polygon>

            <gml:Polygon>
                <gml:exterior>
                    <gml:LinearRing>
                        <gml:pointRep>...</gml:pointRep>
                        ...
                    </gml:LinearRing>
                </gml:exterior>
            </gml:Polygon>
        '''

        polygon_list = self.where_node.findall( '{http://www.opengis.net/gml}Polygon' )
        if polygon_list:
            logger.debug( '  "GML Polygon" detected! Decoding...' )
            for polygon in polygon_list:
                exterior = polygon.find( '{http://www.opengis.net/gml}exterior' )
                interior = polygon.find( '{http://www.opengis.net/gml}interior' )

                polygon_tmp = []
                raw_tmp = ''
                if exterior:
                    ring = ext_.find( '{http://www.opengis.net/gml}LinearRing' )

                    if ring:
                        poslist = ring.find( '{http://www.opengis.net/gml}posList' )
                        # get all pos nodes, if existing
                        pos_list = ring.findall( './/{http://www.opengis.net/gml}pos' )

                        ext_pol = []
                        ext_raw = '('
                        if poslist:
                            tmp = re.sub( '\s+', ' ', poslist.text.strip().replace( ',', ' ' ) ).split()
                            # Gel all Latitudes
                            lat_list = tmp[ 0 : len( tmp ) : 2 ]
                            # Gel all Longitudes
                            lon_list = tmp[ 1 : len( tmp ) : 2 ]

                            for lat, lon in zip( lat_list, lon_list ):
                                ext_pol.append( [ float( lat ), float( lon ) ] )
                                ext_raw += '%s %s,' % ( str( float( lon ) ), str( float( lat ) ) )
                            # remove last comma
                            ext_raw = ext_raw[ 0 : -1 ]

                        if pos_list and len( pos_list ) > 0:
                            for pos in pos_list:
                                tmp = re.sub( '\s+', ' ', pos.text.strip().replace( ',', ' ' ) ).split()
                                ext_pol.append( [ float(  tmp[ 0 ] ), float(  tmp[ 1 ] ) ] )
                                ext_raw += '%s %s,' % ( str( float(  tmp[ 1 ] ) ), str( float(  tmp[ 0 ] ) ) )
                            # remove last comma
                            ext_raw = ext_raw[ 0 : -1 ]
                        ext_raw += ')'

                        polygon_tmp.extend( ext_pol )
                        raw_tmp += ext_raw

                if interior:
                    ring = int_.findall( '{http://www.opengis.net/gml}LinearRing' )

                    if ring:
                        poslist = ring.find( '{http://www.opengis.net/gml}posList' )
                        # get all pos nodes, if existing
                        pos_list = ring.findall( './/{http://www.opengis.net/gml}pos' )

                        int_pol = []
                        int_raw = '('
                        if poslist:
                            tmp = re.sub( '\s+', ' ', poslist.text.strip().replace( ',', ' ' ) ).split()
                            # Gel all Latitudes
                            lat_list = tmp[ 0 : len( tmp ) : 2 ]
                            # Gel all Longitudes
                            lon_list = tmp[ 1 : len( tmp ) : 2 ]

                            for lat, lon in zip( lat_list, lon_list ):
                                int_pol.append( [ float( lat ), float( lon ) ] )
                                int_raw += '%s %s,' % ( str( float( lon ) ), str( float( lat ) ) )
                            # remove last comma
                            int_raw = int_raw[ 0 : -1 ]

                        if pos_list and len( pos_list ) > 0:
                            for pos in pos_list:
                                tmp = re.sub( '\s+', ' ', pos.text.strip().replace( ',', ' ' ) ).split()
                                int_pol.append( [ float(  tmp[ 0 ] ), float(  tmp[ 1 ] ) ] )
                                int_raw += '%s %s,' % ( str( float(  tmp[ 1 ] ) ), str( float(  tmp[ 0 ] ) ) )
                            # remove last comma
                            int_raw = int_raw[ 0 : -1 ]
                        int_raw += ')'

                        polygon_tmp.extend( int_pol )
                        raw_tmp += int_raw

                self.polygon_list.append( {
                    'type': 'POLYGON',
                    'mode': 'latlon',
                    'coordinates': polygon_tmp,
                    'raw': 'POLYGON(%s)' % raw_tmp,
                } )
            return True

        logger.debug( '  No "GML Polygon" detected! Nothing to decode.' )
        return False

    def __gml_boxes( self ):
        '''
        Example:
            <gml:Envelope>
                <gml:lowerCorner>42.943 -71.032</gml:lowerCorner>
                <gml:upperCorner>43.039 -69.856</gml:upperCorner>
            </gml:Envelope>

        The following are DEPRECATED:
            <gml:Envelope>
                <gml:coord>...</gml:coord>
                <gml:coord>...</gml:coord>
            </gml:Envelope>

            <gml:Envelope>
                <gml:pos>...</gml:pos>
                <gml:pos>...</gml:pos>
            </gml:Envelope>

            <gml:Envelope>
                <gml:coordinates>...</gml:coordinates>
            </gml:Envelope>
        '''

        envelope_list = self.where_node.findall( '{http://www.opengis.net/gml}Envelope' )
        if envelope_list:
            logger.debug( '  "GML Box" detected! Decoding...' )
            for envelope in envelope_list:
                lc = envelope.find( '{http://www.opengis.net/gml}lowerCorner' )
                lc_raw = re.sub( '\s+', ' ', lc.text.strip().replace( ',', ' ' ) )
                lc_tmp = lc_raw.split()

                uc = envelope.find( '{http://www.opengis.net/gml}upperCorner' )
                uc_raw = re.sub( '\s+', ' ', uc.text.strip().replace( ',', ' ' ) )
                uc_tmp = uc_raw.split()

                polygon_tmp = []
                polygon_tmp.append( [ float( uc_tmp[ 0 ] ), float( uc_tmp[ 1 ] ) ] )
                polygon_tmp.append( [ float( lc_tmp[ 0 ] ), float( uc_tmp[ 1 ] ) ] )
                polygon_tmp.append( [ float( lc_tmp[ 0 ] ), float( lc_tmp[ 1 ] ) ] )
                polygon_tmp.append( [ float( uc_tmp[ 0 ] ), float( lc_tmp[ 1 ] ) ] )
                polygon_tmp.append( [ float( uc_tmp[ 0 ] ), float( uc_tmp[ 1 ] ) ] )
                raw_tmp = ''
                raw_tmp += '%s %s,' % ( str( float( uc_tmp[ 1 ] ) ), str( float( uc_tmp[ 0 ] ) ) )
                raw_tmp += '%s %s,' % ( str( float( uc_tmp[ 1 ] ) ), str( float( lc_tmp[ 0 ] ) ) )
                raw_tmp += '%s %s,' % ( str( float( lc_tmp[ 1 ] ) ), str( float( lc_tmp[ 0 ] ) ) )
                raw_tmp += '%s %s,' % ( str( float( lc_tmp[ 1 ] ) ), str( float( uc_tmp[ 0 ] ) ) )
                raw_tmp += '%s %s'  % ( str( float( uc_tmp[ 1 ] ) ), str( float( uc_tmp[ 0 ] ) ) )
                self.polygon_list.append( {
                    'type': 'POLYGON',
                    'mode': 'latlon',
                    'coordinates': [ polygon_tmp ],
                    'raw': 'POLYGON((%s))' % raw_tmp,
                } )
            return True

        logger.debug( '  No "GML Box" detected! Nothing to decode.' )
        return False
