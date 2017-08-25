"""
tests.Test
---------------
:copyright: (c) 2017 by Sergio Ferraresi.
:license: Apache2, see LICENSE for more details.
"""

import logging
import unittest
import xml.etree.ElementTree as ET

from api import decode as GeoRssDecoder

class TestGeoRSSy( unittest.TestCase ):

    def test_no_parameters( self ):
        logging.basicConfig( level = logging.ERROR )

        # Check "no parameters" error
        self.assertRaises( ValueError, GeoRssDecoder )

    def test_no_parent_node( self ):
        logging.basicConfig( level = logging.ERROR )

        # Check "parent_node = None" error
        self.assertRaises( ValueError, GeoRssDecoder, parent_node = None )

    def test_no_polygons_over_boxes( self ):
        logging.basicConfig( level = logging.ERROR )

        parent_node = ET.parse( 'georssy/data/tests/test_simple_point.xml' ).getroot()

        # Check "polygons_over_boxes = False" when not specified
        d = GeoRssDecoder( parent_node = parent_node ) # DUMMY parent node
        self.assertEqual( d.polygons_over_boxes, False )


class TestSimpleGeoRSS( unittest.TestCase ):

    def test_simple_point( self ):
        logging.basicConfig( level = logging.ERROR )

        parent_node = ET.parse( 'georssy/data/tests/test_simple_point.xml' ).getroot().find( '{http://www.w3.org/2005/Atom}entry' )

        # Check Simple Point detection
        d = GeoRssDecoder( parent_node = parent_node )
        self.assertIsNotNone( d.point_list )
        self.assertNotEqual( d.point_list, [] )

    def test_simple_line( self ):
        logging.basicConfig( level = logging.ERROR )

        parent_node = ET.parse( 'georssy/data/tests/test_simple_line.xml' ).getroot().find( '{http://www.w3.org/2005/Atom}entry' )

        # Check Simple Line detection
        d = GeoRssDecoder( parent_node = parent_node )
        self.assertIsNotNone( d.line_list )
        self.assertNotEqual( d.line_list, [] )

    def test_simple_polygon( self ):
        logging.basicConfig( level = logging.ERROR )

        parent_node = ET.parse( 'georssy/data/tests/test_simple_polygon.xml' ).getroot().find( '{http://www.w3.org/2005/Atom}entry' )

        # Check Simple Polygon detection
        d = GeoRssDecoder( parent_node = parent_node )
        self.assertIsNotNone( d.polygon_list )
        self.assertNotEqual( d.polygon_list, [] )

    def test_simple_box( self ):
        logging.basicConfig( level = logging.ERROR )

        parent_node = ET.parse( 'georssy/data/tests/test_simple_box.xml' ).getroot().find( '{http://www.w3.org/2005/Atom}entry' )

        # Check Simple Box detection
        d = GeoRssDecoder( parent_node = parent_node )
        self.assertIsNotNone( d.polygon_list )
        self.assertNotEqual( d.polygon_list, [] )

    def test_feature_type( self ):
        logging.basicConfig( level = logging.ERROR )

        parent_node = ET.parse( 'georssy/data/tests/test_simple_point.xml' ).getroot().find( '{http://www.w3.org/2005/Atom}entry' )

        # Check Feature Type detection
        d = GeoRssDecoder( parent_node = parent_node )
        self.assertIsNotNone( d.feature_type_list )
        self.assertNotEqual( d.feature_type_list, [] )

    def test_feature_name( self ):
        logging.basicConfig( level = logging.ERROR )

        parent_node = ET.parse( 'georssy/data/tests/test_simple_point.xml' ).getroot().find( '{http://www.w3.org/2005/Atom}entry' )

        # Check Feature Name detection
        d = GeoRssDecoder( parent_node = parent_node )
        self.assertIsNotNone( d.feature_name_list )
        self.assertNotEqual( d.feature_name_list, [] )

    def test_relationship( self ):
        logging.basicConfig( level = logging.ERROR )

        parent_node = ET.parse( 'georssy/data/tests/test_simple_point.xml' ).getroot().find( '{http://www.w3.org/2005/Atom}entry' )

        # Check Relationship detection
        d = GeoRssDecoder( parent_node = parent_node )
        self.assertIsNotNone( d.relationship_list )
        self.assertNotEqual( d.relationship_list, [] )

    def test_elevation( self ):
        logging.basicConfig( level = logging.ERROR )

        parent_node = ET.parse( 'georssy/data/tests/test_simple_point.xml' ).getroot().find( '{http://www.w3.org/2005/Atom}entry' )

        # Check Elevation detection
        d = GeoRssDecoder( parent_node = parent_node )
        self.assertIsNotNone( d.elevation_list )
        self.assertNotEqual( d.elevation_list, [] )

    def test_floor( self ):
        logging.basicConfig( level = logging.ERROR )

        parent_node = ET.parse( 'georssy/data/tests/test_simple_point.xml' ).getroot().find( '{http://www.w3.org/2005/Atom}entry' )

        # Check Floor detection
        d = GeoRssDecoder( parent_node = parent_node )
        self.assertIsNotNone( d.floor_list )
        self.assertNotEqual( d.floor_list, [] )

    def test_radius( self ):
        logging.basicConfig( level = logging.ERROR )

        parent_node = ET.parse( 'georssy/data/tests/test_simple_point.xml' ).getroot().find( '{http://www.w3.org/2005/Atom}entry' )

        # Check Radius detection
        d = GeoRssDecoder( parent_node = parent_node )
        self.assertIsNotNone( d.radius_list )
        self.assertNotEqual( d.radius_list, [] )


class TestGmlGeoRSS( unittest.TestCase ):

    def test_gml_point( self ):
        logging.basicConfig( level = logging.ERROR )

        parent_node = ET.parse( 'georssy/data/tests/test_gml_point.xml' ).getroot().find( '{http://www.w3.org/2005/Atom}entry' )

        # Check GML Point detection
        d = GeoRssDecoder( parent_node = parent_node )
        self.assertIsNotNone( d.point_list )
        self.assertNotEqual( d.point_list, [] )

    def test_gml_line_1( self ):
        logging.basicConfig( level = logging.ERROR )

        parent_node = ET.parse( 'georssy/data/tests/test_gml_line_1.xml' ).getroot().find( '{http://www.w3.org/2005/Atom}entry' )

        # Check GML Line detection
        d = GeoRssDecoder( parent_node = parent_node )
        self.assertIsNotNone( d.line_list )
        self.assertNotEqual( d.line_list, [] )

    def test_gml_line_2( self ):
        logging.basicConfig( level = logging.ERROR )

        parent_node = ET.parse( 'georssy/data/tests/test_gml_line_2.xml' ).getroot().find( '{http://www.w3.org/2005/Atom}entry' )

        # Check GML Line detection
        d = GeoRssDecoder( parent_node = parent_node )
        self.assertIsNotNone( d.line_list )
        self.assertNotEqual( d.line_list, [] )

    def test_gml_line_3( self ):
        logging.basicConfig( level = logging.ERROR )

        parent_node = ET.parse( 'georssy/data/tests/test_gml_line_3.xml' ).getroot().find( '{http://www.w3.org/2005/Atom}entry' )

        # Check GML Line detection
        d = GeoRssDecoder( parent_node = parent_node )
        self.assertIsNotNone( d.line_list )
        self.assertNotEqual( d.line_list, [] )

    def test_gml_polygon_1( self ):
        logging.basicConfig( level = logging.ERROR )

        parent_node = ET.parse( 'georssy/data/tests/test_gml_polygon_1.xml' ).getroot().find( '{http://www.w3.org/2005/Atom}entry' )

        # Check GML Polygon detection
        d = GeoRssDecoder( parent_node = parent_node )
        self.assertIsNotNone( d.polygon_list )
        self.assertNotEqual( d.polygon_list, [] )

    def test_gml_polygon_2( self ):
        logging.basicConfig( level = logging.ERROR )

        parent_node = ET.parse( 'georssy/data/tests/test_gml_polygon_2.xml' ).getroot().find( '{http://www.w3.org/2005/Atom}entry' )

        # Check GML Polygon detection
        d = GeoRssDecoder( parent_node = parent_node )
        self.assertIsNotNone( d.polygon_list )
        self.assertNotEqual( d.polygon_list, [] )

    def test_gml_polygon_3( self ):
        logging.basicConfig( level = logging.ERROR )

        parent_node = ET.parse( 'georssy/data/tests/test_gml_polygon_3.xml' ).getroot().find( '{http://www.w3.org/2005/Atom}entry' )

        # Check GML Polygon detection
        d = GeoRssDecoder( parent_node = parent_node )
        self.assertIsNotNone( d.polygon_list )
        self.assertNotEqual( d.polygon_list, [] )

    def test_gml_polygon_4( self ):
        logging.basicConfig( level = logging.ERROR )

        parent_node = ET.parse( 'georssy/data/tests/test_gml_polygon_4.xml' ).getroot().find( '{http://www.w3.org/2005/Atom}entry' )

        # Check GML Polygon detection
        d = GeoRssDecoder( parent_node = parent_node )
        self.assertIsNotNone( d.polygon_list )
        self.assertNotEqual( d.polygon_list, [] )

    def test_gml_polygon_5( self ):
        logging.basicConfig( level = logging.ERROR )

        parent_node = ET.parse( 'georssy/data/tests/test_gml_polygon_5.xml' ).getroot().find( '{http://www.w3.org/2005/Atom}entry' )

        # Check GML Polygon detection
        d = GeoRssDecoder( parent_node = parent_node )
        self.assertIsNotNone( d.polygon_list )
        self.assertNotEqual( d.polygon_list, [] )

    def test_gml_polygon_6( self ):
        logging.basicConfig( level = logging.ERROR )

        parent_node = ET.parse( 'georssy/data/tests/test_gml_polygon_6.xml' ).getroot().find( '{http://www.w3.org/2005/Atom}entry' )

        # Check GML Polygon detection
        d = GeoRssDecoder( parent_node = parent_node )
        self.assertIsNotNone( d.polygon_list )
        self.assertNotEqual( d.polygon_list, [] )

    def test_gml_box( self ):
        logging.basicConfig( level = logging.ERROR )

        parent_node = ET.parse( 'georssy/data/tests/test_gml_box.xml' ).getroot().find( '{http://www.w3.org/2005/Atom}entry' )

        # Check GML Box detection
        d = GeoRssDecoder( parent_node = parent_node )
        self.assertIsNotNone( d.polygon_list )
        self.assertNotEqual( d.polygon_list, [] )


if __name__ == "__main__":
    tc_list = ( TestGeoRSSy, TestSimpleGeoRSS, TestGmlGeoRSS )

    ts = unittest.TestSuite()
    for tc in tc_list:
        ts.addTests( unittest.TestLoader().loadTestsFromTestCase( tc ) )

    unittest.TextTestRunner( verbosity = 2 ).run( ts )
