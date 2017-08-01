import flexmock

from ub_object_client import ubersmith_object_api


def test_client_list():
    client_list = flexmock()
    client_list.should_receive('list').and_return({
        "1001": {
            "city": "Troy",
        }
    })

    backend = flexmock(client=client_list)

    object_api = ubersmith_object_api.init(backend=backend)
    returned_object = object_api.client.list()

    assert "Troy" == returned_object[0].city
