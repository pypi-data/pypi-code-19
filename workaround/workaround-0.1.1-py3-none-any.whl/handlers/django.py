import requests

from .base import (
    BaseHandler,
    Workaround,
)


def get_ticket_state(ticket_id):
    response = requests.get('https://code.djangoproject.com/jsonrpc',
                            json={'method': 'ticket.get', 'params': [ticket_id]})
    response.raise_for_status()

    ticket_json = response.json()['result'][3]
    return ticket_json['resolution'], ticket_json['status']


class DjangoHandler(BaseHandler):
    adjectives = {'closed', 'fixed'}
    value_patterns = [
        r'dj(ango)?:(?P<ticket_id>\d+)',
        r'.*code\.djangoproject\.com\/ticket\/(?P<ticket_id>\d+)'
    ]
    example_values = [
        'django:28440',
        'https://code.djangoproject.com/ticket/27849/'
    ]

    def get_result(self, workaround: Workaround, parsed_value):
        return get_ticket_state(parsed_value['ticket_id'])

    def is_result_equal(self, result, adjective):
        return any(r == adjective for r in result)
