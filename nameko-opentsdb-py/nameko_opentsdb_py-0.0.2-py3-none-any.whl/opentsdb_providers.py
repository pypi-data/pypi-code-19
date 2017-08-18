from weakref import WeakKeyDictionary
import time

from nameko.extensions import DependencyProvider, SharedExtension, ProviderCollector
from opentsdb import TSDBClient, Counter, Gauge

__all__ = ['SharedOpenTSDB', 'OpenTSDBBasic', 'OpenTSDB']


class SharedOpenTSDB(ProviderCollector, SharedExtension):
    OPEN_TSDB_CONFIG_KEY = 'TSDB_CONFIG'

    metrics = {}

    def __init__(self, **metrics):
        super(SharedOpenTSDB, self).__init__()
        self.metrics.update(metrics)
        self._client = None

    def get_client(self) -> TSDBClient:
        return self._client

    def start(self):
        self._client = TSDBClient(
            static_tags=self.container.config[self.OPEN_TSDB_CONFIG_KEY]['STATIC_TAGS'],
            **self.container.config[self.OPEN_TSDB_CONFIG_KEY]['OPTIONS'])

        for name, metric in self.metrics.items():
            setattr(self._client, name, metric)

    def stop(self):
        self._client.close()
        self._client.wait()

    def kill(self):
        self._client.close()
        self._client.stop()
        self._client = None


class OpenTSDBBasic(DependencyProvider):

    def __init__(self, **metrics):
        self.shared_opentsdb = SharedOpenTSDB(**metrics)

    def setup(self):
        self.shared_opentsdb.register_provider(self)

    def stop(self):
        self.shared_opentsdb.unregister_provider(self)
        super(OpenTSDBBasic, self).stop()

    def get_dependency(self, worker_ctx):
        return self.shared_opentsdb.get_client()


class OpenTSDB(OpenTSDBBasic):

    NAMEKO_RPC_METRICS = {
        'NAMEKO_RPC_CALL_SUCCESS': Counter('nameko.rpc_call.success', ['method']),
        'NAMEKO_RPC_CALL_FAILED': Counter('nameko.rpc_call.failed', ['method']),
        'NAMEKO_RPC_EXECUTE_TIME': Gauge('nameko.rpc_call.execute_time_ms', ['method'])
    }

    def __init__(self, **metrics):
        metrics.update(self.NAMEKO_RPC_METRICS)
        super().__init__(**metrics)
        self.timestamps = WeakKeyDictionary()

    def worker_setup(self, worker_ctx):
        self.timestamps[worker_ctx] = time.time()

    def worker_result(self, worker_ctx, result=None, exc_info=None):
        service_name = worker_ctx.service_name
        method_name = worker_ctx.entrypoint.method_name

        worker_started = self.timestamps.pop(worker_ctx)
        total_duration = round((time.time() - worker_started)*1000, 4)
        rpc_method = "%s.%s" % (service_name, method_name)

        client = self.shared_opentsdb.get_client()
        if exc_info is None:
            client.NAMEKO_RPC_CALL_SUCCESS.tags(rpc_method).inc()
        else:
            client.NAMEKO_RPC_CALL_FAILED.tags(rpc_method).inc()

        client.NAMEKO_RPC_EXECUTE_TIME.tags(rpc_method).set(total_duration)
