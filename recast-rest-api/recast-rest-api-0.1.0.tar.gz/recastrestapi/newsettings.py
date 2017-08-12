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
PUBLIC_METHODS = ['GET']
PUBLIC_ITEM_METHODS = ['GET']
HATEOAS = True
IF_MATCH = False
PAGINATION_DEFAULT = 1000

ID_FIELD = 'id'
ITEM_LOOKUP_FIELD = ID_FIELD
config.ID_FIELD = ID_FIELD
config.ITEM_LOOKUP_FIELD = ID_FIELD
XML = False
JSON = True

registerSchema('users')(recastdb.models.User)

DOMAIN = {
    'users': recastdb.models.User._eve_schema['users'],
}
