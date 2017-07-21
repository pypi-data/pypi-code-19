from hudai.resource import Resource
from pydash import pick


class MessageResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/messages')
        self.resource_name = 'Message'

    def get(self, message_id):
        return self.request({
            'method': 'GET',
            'params': {'message_id': message_id},
            'url': '/internal/{message_id}'
        })

    def list(self, params):
        return self.request({
            'method': 'GET',
            'params': pick(params, 'sender', 'sent_at', 'subject', 'thread_id'),
            'url': '/internal'
        })

    def create(self, params):
        return self.request({
            'method': 'POST',
            'data': pick(params, 'sender', 'sent_at', 'subject', 'thread_id'),
            'url': '/internal'
        })

    def update(self, params):
        return self.request({
            'method': 'PUT',
            'data': pick(params, 'sender', 'sent_at', 'subject', 'thread_id'),
            'params': pick(params, 'message_id'),
            'url': '/internal/{message_id}'
        })

    def delete(self, message_id):
        return self.request({
            'method': 'DELETE',
            'params': {'message_id': message_id},
            'url': '/internal/{message_id}'
        })
