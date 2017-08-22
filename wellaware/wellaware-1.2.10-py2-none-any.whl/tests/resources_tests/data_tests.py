from __future__ import unicode_literals

from wellaware._compat import array_types
from wellaware.client import Observation, Data, RollupUpdate, RollupUpdateError, RollupUpdateResponse, \
    DataRetrieveError, DataSaveError, DataModificationError, DataRetrieveResponse, DataSaveResponse, \
    DataModificationResponse, HttpError, Point, Token
from wellaware.tests.base import *


class DataTests(BaseClientTestCase):

    token = Token(WA_ADMIN_TOKEN)

    @attr('unit', 'data')
    @responses.activate
    def test_data_save(self):
        resp = {'errors': [
            {'observation': {'email': 'system', 'pointId': 10, 'timestamp': 1234, 'value': 'test'},
             'errorCode': 404, 'errorMessage': 'Not Found'}
        ]}
        responses.add(responses.POST, 'http://localhost/data/create', json=resp, status=200)

        observations = [Observation(point_id=10, value='test', timestamp=1234, email='system')]

        r = Data.save_new_data(self.token, observations=observations)
        self.assertIsInstance(r, DataSaveResponse)
        self.assertEquals(1, len(r.errors))
        e = r.errors[0]
        self.assertIsInstance(e, DataSaveError)
        self.assertEquals(404, e.error_code)
        self.assertEquals('Not Found', e.error_message)
        self.assertIsInstance(e.observation, Observation)
        self.assertEquals(10, e.observation.point_id)
        self.assertEquals('system', e.observation.email)

    @attr('unit', 'data')
    @responses.activate
    def test_data_update(self):
        resp = {'errors': [
            {'observation': {'email': 'system', 'pointId': 10, 'timestamp': 1234, 'value': 'test'},
             'errorCode': 404, 'errorMessage': 'Not Found'}
        ]}
        responses.add(responses.POST, 'http://localhost/data/update', json=resp, status=200)

        observations = [Observation(point_id=10, value='test', timestamp=1234, email='system')]

        r = Data.update_data(self.token, observations=observations)
        self.assertIsInstance(r, DataModificationResponse)
        self.assertEquals(1, len(r.errors))
        e = r.errors[0]
        self.assertIsInstance(e, DataModificationError)
        self.assertEquals(404, e.error_code)
        self.assertEquals('Not Found', e.error_message)
        self.assertIsInstance(e.observation, Observation)
        self.assertEquals(10, e.observation.point_id)
        self.assertEquals('system', e.observation.email)

    @attr('unit', 'data')
    @responses.activate
    def test_data_delete(self):
        resp = {'errors': [
            {'observation': {'email': 'system', 'pointId': 10, 'timestamp': 1234, 'value': 'test'},
             'errorCode': 404, 'errorMessage': 'Not Found'}
        ]}
        responses.add(responses.POST, 'http://localhost/data/delete', json=resp, status=200)

        observations = [Observation(point_id=10, value='test', timestamp=1234, email='system')]

        r = Data.delete_data(self.token, observations=observations)
        self.assertIsInstance(r, DataModificationResponse)
        self.assertEquals(1, len(r.errors))
        e = r.errors[0]
        self.assertIsInstance(e, DataModificationError)
        self.assertEquals(404, e.error_code)
        self.assertEquals('Not Found', e.error_message)
        self.assertIsInstance(e.observation, Observation)
        self.assertEquals(10, e.observation.point_id)
        self.assertEquals('system', e.observation.email)

    @attr('unit', 'data')
    @responses.activate
    def test_data_replay(self):
        resp = {'errors': [
            {'pointId': 10, 'errorCode': 404, 'errorMessage': 'Not Found'}
        ]}
        responses.add(responses.POST, 'http://localhost/data/replay', json=resp, status=200)

        observations = [Observation(point_id=10, value='test', timestamp=1234, email='system')]

        r = Data.replay_data(self.token, point_ids=[10, ])
        self.assertIsInstance(r, DataRetrieveResponse)
        self.assertEquals(1, len(r.errors))
        e = r.errors[0]
        self.assertIsInstance(e, DataRetrieveError)
        self.assertEquals(404, e.error_code)
        self.assertEquals('Not Found', e.error_message)
        self.assertEquals(10, e.point_id)

    @attr('unit', 'data')
    @responses.activate
    def test_data_retrieve(self):
        resp = {'errors': [
            {'pointId': 11, 'errorCode': 404, 'errorMessage': 'Not Found'}
        ], 'observations': {
            '10': [{'timestamp': 12345, 'value': 'test'}]
        }}
        responses.add(responses.POST, 'http://localhost/data/retrieve?start=0&end=100000', json=resp, status=200,
                      match_querystring=True)

        r = Data.retrieve_data(self.token, point_ids=[10, 11], start=0, end=100000)
        self.assertIsInstance(r, DataRetrieveResponse)
        self.assertEquals(1, len(r.errors))
        e = r.errors[0]
        self.assertIsInstance(e, DataRetrieveError)
        self.assertEquals(404, e.error_code)
        self.assertEquals('Not Found', e.error_message)
        self.assertEquals(11, e.point_id)

        self.assertEquals(1, len(r.observations))
        self.assertDictContainsKey(r.observations, 10)
        observations = r.observations.get(10)
        self.assertIsInstance(observations, array_types)
        o = observations[0]
        self.assertIsInstance(o, Observation)
        self.assertEquals(10, o.point_id)
        self.assertEquals('test', o.value)
        self.assertEquals(12345, o.timestamp)

    @attr('unit', 'data')
    @responses.activate
    def test_data_rollup(self):
        resp = {'errors': [
            {'rollupUpdate': {'pointId': 11, 'timestamp': 11}, 'errorCode': 404, 'errorMessage': 'Not Found'}
        ], 'rollupUpdates': {
            '10': [{'timestamp': 10}]
        }}
        responses.add(responses.POST, 'http://localhost/data/rollup', json=resp, status=200, match_querystring=True)

        r = Data.rollup_date(self.token, rollup_updates=[
            RollupUpdate(point_id=10, timestamp=10), RollupUpdate(point_id=11, timestamp=11)
        ])

        self.assertIsInstance(r, RollupUpdateResponse)
        self.assertEquals(1, len(r.errors))
        e = r.errors[0]
        self.assertIsInstance(e, RollupUpdateError)
        self.assertEquals(404, e.error_code)
        self.assertEquals('Not Found', e.error_message)
        e_rollup = e.rollup
        self.assertEquals(11, e_rollup.point_id)
        self.assertEquals(11, e_rollup.timestamp)

        self.assertEquals(1, len(r.rollup_updates))
        self.assertDictContainsKey(r.rollup_updates, 10)
        rollups = r.rollup_updates.get(10)
        self.assertIsInstance(rollups, array_types)
        rollup_update = rollups[0]
        self.assertIsInstance(rollup_update, RollupUpdate)
        self.assertEquals(10, rollup_update.point_id)
        self.assertEquals(10, rollup_update.timestamp)
