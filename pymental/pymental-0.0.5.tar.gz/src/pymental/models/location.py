from pymental.meta import Model

from pymental.fields import GenericField, RelatedField


class AuthenticationDetails(Model):
    authentication_type = GenericField('authentication_type')
    username = GenericField('username')
    password = GenericField('password')
    external_account_id = GenericField('external_account_id')
    external_role_name = GenericField('external_role_name')
    external_id = GenericField('external_id')


class Location(Model):
    _tag = 'location'

    uri = GenericField('uri')
    certificate_file = GenericField('certificate_file')
    authentication_details = RelatedField(
        'authentication_details', AuthenticationDetails)
