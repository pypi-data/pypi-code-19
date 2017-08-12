from recastrestapi.apiconfig import config as apiconf

import recastdb.models
from recastdb.database import db

from eve_sqlalchemy.decorators import registerSchema
from eve.utils import config
from recastrestapi.apiconfig import config as apiconf

DEBUG = True
SQLALCHEMY_DATABASE_URI =  apiconf['RECAST_DBPATH']
AWS_ACCESS_KEY_ID = apiconf['RECAST_AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = apiconf['RECAST_AWS_SECRET_ACCESS_KEY']
AWS_S3_BUCKET_NAME = apiconf['RECAST_AWS_S3_BUCKET_NAME']
RESOURCE_METHODS = ['GET', 'POST', 'DELETE']
ITEM_METHODS = ['GET', 'PUT', 'DELETE']
PUBLIC_METHODS = ['GET']
PUBLIC_ITEM_METHODS = ['GET']
HATEOAS = True
IF_MATCH = False
PAGINATION_DEFAULT = 1000
ID_FIELD = 'id'
ITEM_LOOKUP_FIELD = ID_FIELD
config.ID_FIELD = ID_FIELD
config.ITEM_LOOKUP_FIELD = ID_FIELD
XML = True
JSON = True
EMBEDDING = True

from eve.auth import BasicAuth
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
class TokenAuth(BasicAuth):
	def check_auth(self, orcid_id, token, allowed_roles, resource, method):
		"""
			Token based authentications
		"""
		try:
			user = recastdb.models.User.query.filter(
				recastdb.models.User.orcid_id == orcid_id).one()
			access_token = recastdb.models.AccessToken.query.filter(
				recastdb.models.AccessToken.token == token).one()
			return access_token.user_id == user.id
		except MultipleResultsFound, e:
			return False
		except NoResultFound, e:
			return False

registerSchema('users')(recastdb.models.User)
registerSchema('analysis')(recastdb.models.Analysis)
registerSchema('subscriptions')(recastdb.models.Subscription)
registerSchema('run_conditions')(recastdb.models.RunCondition)
registerSchema('models')(recastdb.models.Model)
registerSchema('scan_requests')(recastdb.models.ScanRequest)
registerSchema('point_requests')(recastdb.models.PointRequest)
registerSchema('basic_requests')(recastdb.models.BasicRequest)
registerSchema('parameters')(recastdb.models.Parameters)
registerSchema('point_coordinates')(recastdb.models.PointCoordinate)
registerSchema('request_archives')(recastdb.models.RequestArchive)
registerSchema('scan_responses')(recastdb.models.ScanResponse)
registerSchema('point_responses')(recastdb.models.PointResponse)
registerSchema('basic_responses')(recastdb.models.BasicResponse)
registerSchema('response_archives')(recastdb.models.ResponseArchive)

DOMAIN = {
    'users': recastdb.models.User._eve_schema['users'],
    'analysis': recastdb.models.Analysis._eve_schema['analysis'],
    'subscriptions': recastdb.models.Subscription._eve_schema['subscriptions'],
    'run_conditions': recastdb.models.RunCondition._eve_schema['run_conditions'],
    'models': recastdb.models.Model._eve_schema['models'],
    'scan_requests': recastdb.models.ScanRequest._eve_schema['scan_requests'],
    'point_requests': recastdb.models.PointRequest._eve_schema['point_requests'],
    'basic_requests': recastdb.models.BasicRequest._eve_schema['basic_requests'],
    'parameters': recastdb.models.Parameters._eve_schema['parameters'],
    'point_coordinates': recastdb.models.PointCoordinate._eve_schema['point_coordinates'],
    'request_archives': recastdb.models.RequestArchive._eve_schema['request_archives'],
    'scan_responses': recastdb.models.ScanResponse._eve_schema['scan_responses'],
    'point_responses': recastdb.models.PointResponse._eve_schema['point_responses'],
    'basic_responses': recastdb.models.BasicResponse._eve_schema['basic_responses'],
    'response_archives': recastdb.models.ResponseArchive._eve_schema['response_archives'],
}

DOMAIN['users'].update({
    'item_lookup_field': 'id',
    'additional_lookup': {
        'url': 'regex("[0-9]+")',
        'field': 'id'
    },
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,
    'resource_methods': ['GET', 'POST', 'DELETE'],
    'item_methods': ['GET', 'PUT', 'PATCH']
})
## prevent email addresses from being returned
DOMAIN['users']['datasource']['projection']['email'] = 0

DOMAIN['analysis'].update({
    'item_lookup_field': 'id',
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,
    'resource_methods': ['GET', 'POST', 'DELETE']
})

DOMAIN['run_conditions'].update({
    'item_lookup_field': 'id',
    'additional_lookup': {
        'url': 'regex("[0-9]+")',
        'field': 'id'
    },
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,
    'resource_methods': ['GET', 'POST', 'DELETE'],
    'item_methods': ['GET', 'PUT', 'PATCH'],
    'resource_methods': ['GET', 'POST', 'DELETE']
})

DOMAIN['request_archives'].update({
    'allow_unknown': True,
    'resource_methods': ['GET', 'POST', 'DELETE'],
    'item_methods': ['GET', 'PUT', 'PATCH'],
})

DOMAIN['response_archives'].update({
    'allow_unknown': True,
    'resource_methods': ['GET', 'POST', 'DELETE'],
    'item_methods': ['GET', 'PUT', 'PATCH'],
})

DOMAIN['scan_requests'].update({
    'item_lookup_field': 'id',
    'additional_lookup': {
        'url': 'regex("[0-9]+")',
        'field': 'id'
    },
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,
    'resource_methods': ['GET', 'POST', 'DELETE'],
    'item_methods': ['GET', 'PUT', 'PATCH'],
    'url': 'scan_requests',
})

DOMAIN['scan_responses'].update({
    'item_lookup_field': 'id',
    'additional_lookup': {
        'url': 'regex("[0-9]+")',
        'field': 'id'
    },
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,
    'resource_methods': ['GET', 'POST', 'DELETE'],
    'item_methods': ['GET', 'PUT', 'PATCH'],
    'url': 'scan_responses',
})

DOMAIN['point_requests'].update({
    'item_lookup_field': 'id',
    'additional_lookup': {
        'url': 'regex("[0-9]+")',
        'field': 'id'
    },
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,
    'resource_methods': ['GET', 'POST', 'DELETE'],
    'item_methods': ['GET', 'PUT', 'PATCH'],
    'allow_unknown': True,
})

DOMAIN['point_responses'].update({
    'item_lookup_field': 'id',
    'additional_lookup': {
        'url': 'regex("[0-9]+")',
        'field': 'id'
    },
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,
    'resource_methods': ['GET', 'POST', 'DELETE'],
    'item_methods': ['GET', 'PUT', 'PATCH'],
    'url': 'point_responses',
})

DOMAIN['basic_requests'].update({
    'item_lookup_field': 'id',
    'additional_lookup': {
        'url': 'regex("[0-9]+")',
        'field': 'id'
    },
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,
    'resource_methods': ['GET', 'POST', 'DELETE'],
    'item_methods': ['GET', 'PUT', 'PATCH'],
    'allow_unknown': True,
})

DOMAIN['basic_responses'].update({
    'item_lookup_field': 'id',
    'additional_lookup': {
        'url': 'regex("[0-9]+")',
        'field': 'id'
    },
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,
    'resource_methods': ['GET', 'POST', 'DELETE'],
    'item_methods': ['GET', 'PUT', 'PATCH'],
    'url': 'basic_responses',
})


# import IPython
# IPython.embed()

DOMAIN['point_coordinates'].update({
    'item_lookup_field': 'id',
    'additional_lookup': {
        'url': 'regex("[0-9]+")',
        'field': 'id'
    },
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,
    'resource_methods': ['GET', 'POST', 'DELETE'],
    'item_methods': ['GET', 'PUT', 'PATCH'],
    'url': 'point_coordinates',
})
