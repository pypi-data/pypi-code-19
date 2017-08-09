import rest_framework_filters as filters

from core_flavor.api import lookups
from ... import models


class ItemFilter(filters.FilterSet):

    class Meta:
        model = models.Item
        fields = {
            'id': ['exact'],
            'title':  lookups.TEXT_LOOKUPS,
            'price': lookups.RANGE_LOOKUPS,
            'created': lookups.DATETIME_LOOKUPS
        }
