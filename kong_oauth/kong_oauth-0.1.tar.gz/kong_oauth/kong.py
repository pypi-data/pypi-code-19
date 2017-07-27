from django.conf import settings
from .resource import API, Resource

class KongAPI(API):
    base_url = getattr(settings, 'KONG_ADMIN_URL', 'https://kong:8001')
    headers = {'content-type':'application/json'}
    # username = getattr(settings, KONG_ADMIN_USERNAME, None)
    # password = getattr(settings, KONG_ADMIN_PASSWORD, None)
    # auth = (username, password)

class ApiResource(Resource):
    api_class = KongAPI
    resource_path = "/apis"

class ConsumerResource(Resource):
    api_class = KongAPI
    resource_path = "/consumers"

class ConsumerCredentialResource(Resource):
    api_class = KongAPI
    resource_path = "/consumers/{consumer_id}/{plugin}"

class GlobalPluginResource(Resource):
    api_class = KongAPI
    resource_path = "/plugins"

class ApiPluginResource(Resource):
    api_class = KongAPI
    resource_path = "/plugins/{api_id}/plugins"