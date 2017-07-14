from foundrybot.resource import Resource
from pydash import pick


class WebhookSettingResource(Resource):
    def __init__(self, secret_key):
        super(secret_key)
        self.resource_name = 'UrlSnapshotTag'

    def subscribe(self, params):
        return self.make_request({
            'method': 'POST',
            'data': pick(params, 'type', 'urlEndpoint'),
            'url': '/webhook-settings/subscribe'
        })

    def unsubscribe(self, params):
        return self.make_request({
            'method': 'POST',
            'data': pick(params, 'type'),
            'url': '/webhook-settings/unsubscribe'
        })