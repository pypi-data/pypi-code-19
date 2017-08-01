from ub_object_client.client import Client


def init(backend):
    return UbersmithObjectApi(backend=backend)


class UbersmithObjectApi(object):
    def __init__(self, backend):
        self.backend = backend

    @property
    def client(self):
        return ClientApi(self.backend)


class ClientApi(object):
    def __init__(self, backend):
        self.backend = backend

    def list(self):
        client_list = self.backend.client.list()
        result = []
        for client_id, client_dict in client_list.items():
            result.append(_patch_matching_attributes(Client(), client_dict))
        return result


def _patch_matching_attributes(client, attributes):
    for k, v in attributes.items():
        if hasattr(client, k):
            setattr(client, k, v)
    return client
