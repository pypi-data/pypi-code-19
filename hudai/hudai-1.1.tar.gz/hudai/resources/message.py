from hudai.resource import Resource
from pydash import pick


class MessageResource(Resource):
    def __init__(self, secret_key):
        Resource.__init__(self, secret_key)
        self.resource_name = 'Message'

    def get(self, message_id):
        return self.make_request({
            'method': 'GET',
            'params': {'message_id': message_id},
            'url': '/messages/internal/{message_id}'
        })

    def search(self, params):
        return self.make_request({
            'method': 'GET',
            'params': pick(params, 'sender', 'sent_at', 'subject', 'thread_id'),
            'url': '/messages/internal'
        })

    def create(self, params):
        return self.make_request({
            'method': 'POST',
            'data': pick(params, 'sender', 'sent_at', 'subject', 'thread_id'),
            'url': '/messages/internal'
        })

    def update(self, params):
        return self.make_request({
            'method': 'PUT',
            'data': pick(params, 'sender', 'sent_at', 'subject', 'thread_id'),
            'params': pick(params, 'message_id'),
            'url': '/messages/internal/{message_id}'
        })

    def delete(self, message_id):
        return self.make_request({
            'method': 'DELETE',
            'params': {'message_id': message_id},
            'url': '/messages/internal/{message_id}'
        })
