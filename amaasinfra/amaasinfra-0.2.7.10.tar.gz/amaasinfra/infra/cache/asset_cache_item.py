import os
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, BooleanAttribute

class AssetCacheItem(Model):
    """
    Cached record for asset
    """
    class Meta:
        environment = os.environ.get('AWS_ENV') or 'dev'
        region = os.environ.get('AWS_DEFAULT_REGION', 'ap-southeast-1')
        table_name = "asset-cache-{}".format(environment)
    asset_id = UnicodeAttribute(hash_key=True)
    asset_manager_id = UnicodeAttribute(range_key=True)
    asset_class = UnicodeAttribute(null=False)
    asset_type = UnicodeAttribute(null=False)
    asset_status = UnicodeAttribute(null=False)
    fungible = BooleanAttribute()
    updated_time = UnicodeAttribute(null=False)
    hash_value = UnicodeAttribute(null=False)
