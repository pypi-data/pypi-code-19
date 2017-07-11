# -*- coding: utf-8 -*-
import unittest
import responses
import json

try:
    from unittest.mock import Mock, patch, MagicMock
except:
    from mock import Mock, patch, MagicMock

from oe_geoutils.utils import (
    convert_geojson_to_wktelement,
    get_srid_from_geojson,
    convert_wktelement_to_geojson,
    get_centroid_xy,
    nearest_location,
    check_in_flanders,
    check_within_flanders,
    AdminGrenzenClient,
    remove_dupl_values,
    remove_dupl_coords,
    provincie_niscode)

try:
    from __init__ import text_, mock_geozoekdiensten_response, mock_geozoekdiensten_get_gemeente_response, \
        get_gemeente_results, get_provincie_results
except:
    from tests import text_, mock_geozoekdiensten_response, mock_geozoekdiensten_get_gemeente_response, \
        get_gemeente_results, get_provincie_results

try:
    from tests import testdata
except:
    import testdata
import pytest


integration = pytest.mark.skipif(
    not pytest.config.getoption("--integration"),
    reason="need --integration option to run"
)

niscode_url = 'https://test-geo.onroerenderfgoed.be/zoekdiensten/administratievegrenzen'


class GeoUtilTests(unittest.TestCase):
    geojson_valid = {
        "type": "MultiPolygon",
        "coordinates": [[[[152184.01399999947, 212331.8648750011], [152185.94512499947, 212318.6137500011],
                          [152186.13837499946, 212318.6326250011], [152186.86699999947, 212313.9570000011],
                          [152186.91462499945, 212313.65187500112], [152192.45099999948, 212314.2943750011],
                          [152190.69212499948, 212319.2656250011], [152199.58799999946, 212319.5248750011],
                          [152197.85312499947, 212327.9388750011], [152197.57199999946, 212327.8978750011],
                          [152197.08099999945, 212333.2668750011], [152184.01399999947, 212331.8648750011]]]],
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:EPSG::31370"
            }
        }
    }

    def test_geojson_none(self):
        self.assertEqual(None, get_srid_from_geojson(None))

    def test_geojson_value_error(self):
        geojson = {"type": "MultiPolygon",
                   "coordinates": [[]],
                   "crs": {
                       "type": "wrong value",
                       "properties": {
                           "name": "urn:ogc:def:crs:EPSG::31370"
                       }
                   }}

        self.assertRaises(ValueError, convert_geojson_to_wktelement, geojson)

    def test_conversions(self):
        self.assertIsNone(convert_wktelement_to_geojson(None))
        test_wktelement = convert_geojson_to_wktelement(testdata.test_geojson_valid)
        test_geojson_converted = convert_wktelement_to_geojson(test_wktelement)
        self.assertEqual(testdata.test_geojson_valid['type'], test_geojson_converted['type'])
        self.assertEqual(len(testdata.test_geojson_valid['coordinates']), len(test_geojson_converted['coordinates']))
        self.assertEqual(testdata.test_geojson_valid['crs']['type'], test_geojson_converted['crs']['type'])
        self.assertEqual(testdata.test_geojson_valid['crs']['properties']['name'],
                         test_geojson_converted['crs']['properties']['name'])

    def test_wktelement_attribute_error(self):
        wktelement = "string"
        self.assertRaises(AssertionError, convert_wktelement_to_geojson, wktelement)

    def test_get_centroid_polygon(self):
        self.assertEqual('172928.1839066983,174844.0219267663', get_centroid_xy(testdata.test_geojson_valid_polygon))

    def test_get_centroid(self):
        self.assertEqual('172928.1839066983,174844.0219267663', get_centroid_xy(testdata.test_geojson_valid))

    def test_get_centroid_2(self):
        self.assertEqual('152191.3046633389,212324.6399979071', get_centroid_xy(testdata.test_geojson_mulipolygon))

    @integration
    def test_closed_crab_location(self):
        closed_adres = {'omschrijving_straat': u'Fonteinstraat, 75', 'huisnummer': u'75', 'straat': u'Fonteinstraat',
                        'postcode': u'3000', 'gemeente': u'Leuven', 'land': 'BE'}
        self.assertDictEqual(closed_adres, nearest_location(testdata.test_geojson_valid))

    @responses.activate
    def test_closed_crab_location_mock(self):
        responses.add(
            responses.GET,
            'https://loc.geopunt.be/geolocation/Location',
            body='{"LocationResult":[{"ID":201984,"FormattedAddress":"Fonteinstraat 75, 3000 Leuven","Location":{"Lat_WGS84":50.883485330273977,"Lon_WGS84":4.6941590167952487,"X_Lambert72":172899.0,"Y_Lambert72":174842.0},"LocationType":"crab_huisnummer_afgeleidVanGebouw","BoundingBox":{"LowerLeft":{"Lat_WGS84":50.883485330273977,"Lon_WGS84":4.6941590167952487,"X_Lambert72":172899.0,"Y_Lambert72":174842.0},"UpperRight":{"Lat_WGS84":50.883485330273977,"Lon_WGS84":4.6941590167952487,"X_Lambert72":172899.0,"Y_Lambert72":174842.0}}}]}',
            status=200)
        closed_adres = {'omschrijving_straat': u'Fonteinstraat, 75', 'huisnummer': u'75', 'straat': u'Fonteinstraat',
                        'postcode': u'3000', 'gemeente': u'Leuven', 'land': 'BE'}
        self.assertDictEqual(closed_adres, nearest_location(testdata.test_geojson_valid))

    @integration
    def test_closed_crab_location_2(self):
        closed_adres = {'straat': 'Krijgsbaan', 'land': 'BE', 'postcode': '2100',
                         'omschrijving_straat': 'Krijgsbaan, 150', 'huisnummer': '150', 'gemeente': 'Antwerpen'}
        self.assertDictEqual(closed_adres, nearest_location(
            {"type": "MultiPolygon",
             "coordinates": [[[[158788, 211982], [158789, 211982], [158789, 211983], [158788, 211982]]]],
             "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::31370"}}}))

    @responses.activate
    def test_closed_crab_location_2_mock(self):
        responses.add(
            responses.GET,
            'https://loc.geopunt.be/geolocation/Location',
            body='{"LocationResult":[{"ID":3884086,"FormattedAddress":"Krijgsbaan 150, 2100 Antwerpen (2100)","Location":{"Lat_WGS84":51.217719624709794,"Lon_WGS84":4.49453430920374,"X_Lambert72":158788.0,"Y_Lambert72":211982.0},"LocationType":"crab_huisnummer_afgeleidVanPerceelGrb","BoundingBox":{"LowerLeft":{"Lat_WGS84":51.217719624709794,"Lon_WGS84":4.49453430920374,"X_Lambert72":158788.0,"Y_Lambert72":211982.0},"UpperRight":{"Lat_WGS84":51.217719624709794,"Lon_WGS84":4.49453430920374,"X_Lambert72":158788.0,"Y_Lambert72":211982.0}}}]}',
            status=200)
        closed_adres = {'straat': 'Krijgsbaan', 'land': 'BE', 'postcode': '2100',
                         'omschrijving_straat': 'Krijgsbaan, 150', 'huisnummer': '150', 'gemeente': 'Antwerpen'}
        self.assertDictEqual(closed_adres, nearest_location(
            {"type": "MultiPolygon",
             "coordinates": [[[[158788, 211982], [158789, 211982], [158789, 211983], [158788, 211982]]]],
             "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::31370"}}}))

    @integration
    def test_closed_crab_location_none(self):
        self.assertIsNone(nearest_location(testdata.test_json_intersects_flanders))

    @responses.activate
    def test_closed_crab_location_none_mock(self):
        responses.add(
            responses.GET,
            'https://loc.geopunt.be/geolocation/Location',
            body='{"LocationResult":[{"ID":1031530,"FormattedAddress":"Linkebeekstraat 35, 1180 Ukkel","Location":{"Lat_WGS84":50.779580783177835,"Lon_WGS84":4.327986356112306,"X_Lambert72":147125.0,"Y_Lambert72":163234.0},"LocationType":"urbis_huisnummer","BoundingBox":{"LowerLeft":{"Lat_WGS84":50.779580783177835,"Lon_WGS84":4.327986356112306,"X_Lambert72":147125.0,"Y_Lambert72":163234.0},"UpperRight":{"Lat_WGS84":50.779580783177835,"Lon_WGS84":4.327986356112306,"X_Lambert72":147125.0,"Y_Lambert72":163234.0}}}]}',
            status=200)
        self.assertIsNone(nearest_location(testdata.test_json_intersects_flanders))

    @integration
    def test_closed_crab_location_False(self):
        self.assertFalse(nearest_location(testdata.test_json_outside_flanders))

    @responses.activate
    def test_closed_crab_location_False_mock(self):
        responses.add(
            responses.GET,
            'https://loc.geopunt.be/geolocation/Location',
            body='{"LocationResult":[{"ID":1206833,"FormattedAddress":"Opperstraat 108, 1050 Elsene","Location":{"Lat_WGS84":50.830774347520865,"Lon_WGS84":4.362151535734923,"X_Lambert72":149535.0,"Y_Lambert72":168928.0},"LocationType":"urbis_huisnummer","BoundingBox":{"LowerLeft":{"Lat_WGS84":50.830774347520865,"Lon_WGS84":4.362151535734923,"X_Lambert72":149535.0,"Y_Lambert72":168928.0},"UpperRight":{"Lat_WGS84":50.830774347520865,"Lon_WGS84":4.362151535734923,"X_Lambert72":149535.0,"Y_Lambert72":168928.0}}}]}',
            status=200)
        self.assertFalse(nearest_location(testdata.test_json_outside_flanders))

    @integration
    def test_closesr_crab_location_crabpy_gateway(self):
        n75 = Mock()
        n75.id = 102
        n75.huisnummer = "75"
        fonteinstraat = Mock()
        fonteinstraat.id = 101
        fonteinstraat.label = "Fonteinstraat"
        fonteinstraat.huisnummers = [n75]
        leuven = Mock()
        leuven.id = 100
        leuven.naam = "Leuven"
        leuven.straten = [fonteinstraat]
        gemeenten = [leuven]
        crabpy_gateway = Mock()
        crabpy_gateway.list_gemeenten = Mock(return_value=gemeenten)
        closed_adres = {'omschrijving_straat': u'Fonteinstraat, 75', 'huisnummer': u'75', 'huisnummer_id': 102,
                        'straat': u'Fonteinstraat', 'straat_id': 101,
                        'postcode': u'3000', 'gemeente': u'Leuven', 'gemeente_id': 100, 'land': 'BE'}
        self.assertDictEqual(closed_adres, nearest_location(testdata.test_geojson_valid, crabpy_gateway))

    @responses.activate
    def test_closesr_crab_location_crabpy_gateway_mock(self):
        responses.add(
            responses.GET,
            'https://loc.geopunt.be/geolocation/Location',
            body='{"LocationResult":[{"ID":201984,"FormattedAddress":"Fonteinstraat 75, 3000 Leuven","Location":{"Lat_WGS84":50.883485330273977,"Lon_WGS84":4.6941590167952487,"X_Lambert72":172899.0,"Y_Lambert72":174842.0},"LocationType":"crab_huisnummer_afgeleidVanGebouw","BoundingBox":{"LowerLeft":{"Lat_WGS84":50.883485330273977,"Lon_WGS84":4.6941590167952487,"X_Lambert72":172899.0,"Y_Lambert72":174842.0},"UpperRight":{"Lat_WGS84":50.883485330273977,"Lon_WGS84":4.6941590167952487,"X_Lambert72":172899.0,"Y_Lambert72":174842.0}}}]}',
            status=200)
        n75 = Mock()
        n75.id = 102
        n75.huisnummer = "75"
        fonteinstraat = Mock()
        fonteinstraat.id = 101
        fonteinstraat.label = "Fonteinstraat"
        fonteinstraat.huisnummers = [n75]
        leuven = Mock()
        leuven.id = 100
        leuven.naam = "Leuven"
        leuven.straten = [fonteinstraat]
        gemeenten = [leuven]
        crabpy_gateway = Mock()
        crabpy_gateway.list_gemeenten = Mock(return_value=gemeenten)
        closed_adres = {'omschrijving_straat': u'Fonteinstraat, 75', 'huisnummer': u'75', 'huisnummer_id': 102,
                        'straat': u'Fonteinstraat', 'straat_id': 101,
                        'postcode': u'3000', 'gemeente': u'Leuven', 'gemeente_id': 100, 'land': 'BE'}
        self.assertDictEqual(closed_adres, nearest_location(testdata.test_geojson_valid, crabpy_gateway))

    def test_check_in_flanders(self):
        self.assertTrue(check_in_flanders(testdata.test_geojson_valid))
        self.assertTrue(check_in_flanders(testdata.test_json_intersects_flanders))
        self.assertFalse(check_in_flanders(testdata.test_json_outside_flanders))

    def test_check_within_flanders(self):
        self.assertTrue(check_within_flanders(testdata.test_geojson_valid))
        self.assertFalse(check_within_flanders(testdata.test_json_intersects_flanders))
        self.assertFalse(check_within_flanders(testdata.test_json_outside_flanders))

    def test_convert_geojson_to_wktelement_none(self):
        self.assertIsNone(convert_geojson_to_wktelement(None))

    @responses.activate
    def test_admin_grenzen_client(self):
        base_url = mock_geozoekdiensten_response()
        gemeenten = AdminGrenzenClient(base_url).get_gemeenten(self.geojson_valid)
        self.assertIsInstance(gemeenten, list)
        self.assertGreater(len(gemeenten), 0)

    @responses.activate
    def test_admin_grenzen_client_outside_flanders(self):
        base_url = mock_geozoekdiensten_response()
        gemeenten = AdminGrenzenClient(base_url).get_gemeenten(testdata.test_json_outside_flanders)
        self.assertIsInstance(gemeenten, list)
        self.assertEqual(len(gemeenten), 0)

    @responses.activate
    def test_admin_grenzen_client_raise_service_error(self):
        base_url = mock_geozoekdiensten_response(response_status=500)
        with self.assertRaises(Exception) as ex:
            AdminGrenzenClient(base_url).get_gemeenten(self.geojson_valid)

    @responses.activate
    def test_get_gemeente_2(self):
        base_url = mock_geozoekdiensten_get_gemeente_response(len_results=2)
        gemeente = AdminGrenzenClient(base_url).get_gemeente(testdata.test_geojson_mulipolygon)
        self.assertDictEqual({'naam': 'Antwerpen', 'niscode': '11002'}, gemeente)

    @responses.activate
    def test_get_gemeente_1(self):
        base_url = mock_geozoekdiensten_get_gemeente_response(len_results=1)
        gemeente = AdminGrenzenClient(base_url).get_gemeente(testdata.test_geojson_mulipolygon)
        self.assertDictEqual({'naam': 'gemeente', 'niscode': 'niscode'}, gemeente)

    @responses.activate
    def test_get_gemeente_0(self):
        base_url = mock_geozoekdiensten_get_gemeente_response(len_results=0)
        gemeente = AdminGrenzenClient(base_url).get_gemeente(testdata.test_geojson_mulipolygon)
        self.assertIsNone(gemeente)

    @responses.activate
    def test_get_provincie(self):
        base_url = 'http://geozoekdienst.en/provincies'
        responses.add(responses.POST, base_url, body=json.dumps(get_provincie_results))
        provincie = AdminGrenzenClient(base_url).get_provincie(testdata.test_geojson_mulipolygon)
        self.assertDictEqual({'naam': 'Antwerpen', 'niscode': '10000'}, provincie)

    @responses.activate
    def test_get_provincies(self):
        base_url = 'http://geozoekdienst.en/provincies'
        responses.add(responses.POST, base_url, body=json.dumps(get_provincie_results))
        provincies = AdminGrenzenClient(base_url).get_provincies(testdata.test_geojson_mulipolygon)
        self.assertListEqual(['Antwerpen', 'Vlaams Brabant'], provincies)

    def test_remove_dupl_values_simple(self):
        a = [1, 1, 1, 2, 2, 3, 3, 3, 4, 4, 5, 1]
        remove_dupl_values(a)
        self.assertEqual([1, 2, 3, 4, 5, 1], a)

    def test_remove_dupl_values(self):
        a = [[94826.49908124168, 193977.986615351],
             [94826.49908124168, 193976.986615351],
             [94826.49908124168, 193976.986615351],
             [94820.99908124168, 193974.486615351],
             [94824.99908124168, 193967.986615351],
             [94830.99908124168, 193972.986615351],
             [94826.49908124168, 193977.986615351]]
        remove_dupl_values(a)
        self.assertEqual(
            [[94826.49908124168, 193977.986615351],
             [94826.49908124168, 193976.986615351],
             [94820.99908124168, 193974.486615351],
             [94824.99908124168, 193967.986615351],
             [94830.99908124168, 193972.986615351],
             [94826.49908124168, 193977.986615351]], a)

    def test_remove_dupl_coords(self):
        a = {
            "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::31370"}},
            "type": "MultiPolygon",
            "coordinates": [
                [
                    [
                        [94826.49908124168, 193977.986615351],
                        [94826.49908124168, 193976.986615351],
                        [94826.49908124168, 193976.986615351],
                        [94820.99908124168, 193974.486615351],
                        [94824.99908124168, 193967.986615351],
                        [94830.99908124168, 193972.986615351],
                        [94826.49908124168, 193977.986615351]
                    ]
                ]
            ]
        }
        remove_dupl_coords(a["coordinates"])
        self.assertEqual(
            [[[[94826.49908124168, 193977.986615351],
               [94826.49908124168, 193976.986615351],
               [94820.99908124168, 193974.486615351],
               [94824.99908124168, 193967.986615351],
               [94830.99908124168, 193972.986615351],
               [94826.49908124168, 193977.986615351]]]], a["coordinates"])

    def test_provincie_niscode(self):
        pniscode = provincie_niscode(12021)
        self.assertEqual(10000, pniscode)

    def test_provincie_niscode_vlb(self):
        pniscode = provincie_niscode(24062)
        self.assertEqual(20001, pniscode)
