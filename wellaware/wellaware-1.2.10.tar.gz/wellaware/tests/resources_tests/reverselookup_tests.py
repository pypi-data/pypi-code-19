from __future__ import unicode_literals

from wellaware.client import ReverseLookup, ReverseLookups, MultiReverseLookup, HttpError, Point, Token
from wellaware.tests.base import *


class ReverseLookupTests(BaseClientTestCase):

    token = Token(WA_ADMIN_TOKEN)

    @attr('unit', 'reverselookups')
    @responses.activate
    def test_single_reverse_lookup(self):
        reverse_lookup = ReverseLookup(tenant_id=100, tenant_uuid='12345', entity_type='point',
                                       entity={'name': 'Test Point', 'timezone': 'America/Chicago',
                                               'pointType': 'VOLTAGE', 'dataType': 'double', 'isHidden': False,
                                               'id': 10})
        resp = {'tenantId': 100, 'tenantUuid': '12345', 'type': 'point',
                'entity': {'name': 'Test Point', 'timezone': 'America/Chicago', 'pointType': 'VOLTAGE',
                           'dataType': 'double', 'isHidden': False, 'id': 10}}
        responses.add(responses.GET, 'http://localhost/reverselookup/?id=10&expand=True', json=resp, status=200,
                      match_querystring=True)

        e = ReverseLookups.lookup(self.token, entity_id=10, expand=True)
        self.assertIsInstance(e, ReverseLookup)
        self.assertEquals(100, e.tenant_id)
        self.assertEquals('12345', e.tenant_uuid)
        self.assertEquals('point', e.entity_type)
        p = e.get_entity_as(entity_class=Point)
        self.assertIsInstance(p, Point)
        self.assertEquals(10, p.id)
        self.assertEquals('America/Chicago', p.timezone)
        self.assertEquals('Test Point', p.name)
        self.assertEquals('VOLTAGE', p.point_type)
        self.assertEquals('double', p.data_type)
        self.assertFalse(p.is_hidden)

    @attr('unit', 'reverselookups')
    @responses.activate
    def test_multi_reverse_lookup(self):
        reverse_lookup = ReverseLookup(tenant_id=100, tenant_uuid='12345', entity_type='point',
                                       entity={'name': 'Test Point', 'timezone': 'America/Chicago',
                                               'pointType': 'VOLTAGE', 'dataType': 'double', 'isHidden': False,
                                               'id': 10})
        multi_reverse_lookup = MultiReverseLookup(
            lookups=[reverse_lookup],
            errorIds={'11': HttpError(error_code=404, error_message="Not Found")}
        )

        resp = {'lookups': [
            {'tenantId': 100, 'tenantUuid': '12345', 'type': 'point',
             'entity': {'name': 'Test Point', 'timezone': 'America/Chicago', 'pointType': 'VOLTAGE',
                        'dataType': 'double', 'isHidden': False, 'id': 10}}],
            'errorIds': {'11': {'errorCode': 404, 'errorMessage': 'Not Found'}}
        }
        responses.add(responses.POST, 'http://localhost/reverselookup/?expand=True', json=resp, status=200,
                      match_querystring=True)

        e = ReverseLookups.multi_lookup(self.token, entity_ids=[10, 11], expand=True)
        self.assertIsInstance(e, MultiReverseLookup)
        self.assertEquals(1, len(e.lookups))
        self.assertEquals(1, len(e.error_ids))

        # Check lookup
        rl = e.lookups[0]
        self.assertIsInstance(rl, ReverseLookup)
        self.assertEquals(100, rl.tenant_id)
        self.assertEquals('12345', rl.tenant_uuid)
        self.assertEquals('point', rl.entity_type)
        p = rl.get_entity_as(entity_class=Point)
        self.assertIsInstance(p, Point)
        self.assertEquals(10, p.id)
        self.assertEquals('America/Chicago', p.timezone)
        self.assertEquals('Test Point', p.name)
        self.assertEquals('VOLTAGE', p.point_type)
        self.assertEquals('double', p.data_type)
        self.assertFalse(p.is_hidden)

        # Check errors
        error_id = e.error_ids.get(11)
        self.assertDictContainsKey(e.error_ids, 11)
        self.assertIsInstance(error_id, HttpError)
        self.assertEquals(404, error_id.error_code)
        self.assertEquals('Not Found', error_id.error_message)
