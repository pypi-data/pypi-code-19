import os
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, BooleanAttribute

class AssetCacheItem(Model):
    """
    Cached record for asset
    """
    def __init__(self, hash_key=None, range_key=None, **attrs):
        super().__init__(hash_key=hash_key, range_key=range_key, attrs=attrs)
        self.asset_id = UnicodeAttribute(hash_key=True)
        self.asset_manager_id = UnicodeAttribute(range_key=True)
        self.asset_class = UnicodeAttribute(null=False)
        self.asset_type = UnicodeAttribute(null=False)
        self.asset_status = UnicodeAttribute(null=False)
        self.fungible = BooleanAttribute()
        self.hashcode = UnicodeAttribute(null=False)
        self.updated_time = UnicodeAttribute(null=False)    
        
    class Meta(type):
        def __init__(self):
            self.environment = os.environ.get('AWS_ENV') or 'dev'
            self.region = os.environ.get('AWS_DEFAULT_REGION', 'ap-southeast-1')
            self.table_name = "asset-cache-{}".format(self.environment.lower())
    