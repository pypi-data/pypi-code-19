import os
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute

class AssetIdentity(Model):
    """
    Represents an asset identity in the form of a hash
    """
    class Meta:
        environment = os.environ.get('AWS_ENV') or 'local'
        table_name = "asset-identity-{}".format(environment)
    asset_id = UnicodeAttribute(hash_key=True)
    asset_class = UnicodeAttribute(range_key=True)
    hash_value = UnicodeAttribute(null=False)
