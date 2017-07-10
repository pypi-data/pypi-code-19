
from . import _VDAPIService, _VDDuplicateableResponse

class _SupplyTagAPI(_VDAPIService):

    __RESPONSE_OBJECT__ = _VDDuplicateableResponse
    __API__ = "supply_tags"


class _SupplyPartnerAPI(_VDAPIService):

    __API__ = "supply_partners"

class _SupplyGroupAPI(_VDAPIService):

    __API__ = "supply_groups"



