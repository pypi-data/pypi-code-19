from expects import expect
from icdiff_expects import equal

import striemann.metrics


class Test:

    def test_in_memory(self):
        transport = striemann.metrics.InMemoryTransport()
        metrics = striemann.metrics.Metrics(transport, source='test')
        metrics.recordGauge('service_name', 2., tags=['spam'], ham='eggs')
        metrics.recordGauge('service_name', 4., tags=['spam'], ham='eggs')
        metrics.incrementCounter(
            'service_name', value=5, tags=['foo'], bar='baz'
        )
        metrics.flush()
        expect(transport.last_batch).to(equal([
            {'attributes': {'ham': 'eggs', 'source': 'test'},
             'metric_f': 2.0,
             'service': 'service_name.min',
             'tags': ['spam']},
            {'attributes': {'ham': 'eggs', 'source': 'test'},
             'metric_f': 4.0,
             'service': 'service_name.max',
             'tags': ['spam']},
            {'attributes': {'ham': 'eggs', 'source': 'test'},
             'metric_f': 3.0,
             'service': 'service_name.mean',
             'tags': ['spam']},
            {'attributes': {'ham': 'eggs', 'source': 'test'},
             'metric_f': 2,
             'service': 'service_name.count',
             'tags': ['spam']},
            {'attributes': {'bar': 'baz', 'source': 'test'},
             'metric_f': 5,
             'service': 'service_name',
             'tags': ['foo']}
        ]))
