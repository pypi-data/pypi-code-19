import json
from grpc.beta.implementations import insecure_channel as create_grpc_channel
import segment_source.domain_pb2 as service
from segment_source.stats import Stats
from segment_source.lsp import SourceLogger

_TIMEOUT = 10

channel = create_grpc_channel('localhost', 4000)
client = service.beta_create_Source_stub(channel)
stats = Stats()
lsp = SourceLogger(client, "", "")

##
# Helpers
##

def _byteify(d):
    json_str = json.dumps(d)
    bytes_ = json_str.encode()

    return bytes_

##
# API
##

def set(collection, id_, properties):
    _properties = _byteify(properties)
    request = service.SetRequest(collection=collection, id=id_, properties=_properties)
    stats.incr("set")
    client.Set(request, _TIMEOUT)


def track(context=None, integrations=None, properties=None, anonymous_id=None,
          user_id=None, event=None):
    pass


def identify(context=None, integrations=None, traits=None, anonymous_id=None,
             user_id=None):
    pass


def group(context=None, integrations=None, traits=None, anonymous_id=None,
          user_id=None, event=None):
    pass


def keep_alive():
    stats.incr("keep_alive")
    client.KeepAlive(service.Empty(), _TIMEOUT)


def get_context(allow_failed=False):
    request = service.GetContextRequest(allowFailed=allow_failed)
    return client.GetContext(request, _TIMEOUT).data


def get_context_into_file(allow_failed=False):
    request = service.GetContextIntoFileRequest(allowFailed=allow_failed)
    return client.GetContextIntoFile(request, _TIMEOUT).filename


def store_context(payload):
    request = service.StoreContextRequest(payload=payload)
    client.StoreContext(request, _TIMEOUT)


def store_context_from_file(filename):
    request = service.StoreContextFromFileRequest(filename=filename)
    client.StoreContextFromFile(request, _TIMEOUT)


def report_error(message, collection=None):
    request = service.ReportErrorRequest(message=message, collection=collection)
    client.ReportError(request, _TIMEOUT)


def report_warning(message, collection=None):
    request = service.ReportWarningRequest(message=message, collection=collection)
    client.ReportWarning(request, _TIMEOUT)


def stats_increment(name, value=1, tags=None):
    request = service.StatsRequest(name=name, value=value, tags=tags)
    client.stats_increment(request, _TIMEOUT)


def stats_histogram(name, value, tags=None):
    request = service.StatsRequest(name=name, value=value, tags=tags)
    client.stats_histogram(request, _TIMEOUT)


def stats_gauge(name, value, tags=None):
    request = service.StatsRequest(name=name, value=value, tags=tags)
    client.stats_gauge(request, _TIMEOUT)


def log():
    return stats.log()


def last_touched():
    return stats.last_touched
