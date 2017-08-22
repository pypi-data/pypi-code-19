from __future__ import unicode_literals

from wellaware._compat import add_metaclass
from wellaware.base import BaseAbstractEntity, BaseEntityMetaType, JsonProperty


@add_metaclass(BaseEntityMetaType)
class HttpError(BaseAbstractEntity):
    """
    A Generic Error message.
    """

    error_code = JsonProperty('errorCode')
    error_message = JsonProperty('errorMessage')


__all__ = ['HttpError']
