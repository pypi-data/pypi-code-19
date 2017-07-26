import logging

from .base import BaseRepresentation
from ..schema import UserSchema
from ...api import UserResourceItem

logger = logging.getLogger(__name__)


class UserRepresentation(BaseRepresentation):
    """ UserRepresentation is only used for server

    """

    SCHEMA = UserSchema
    RESOURCE = UserResourceItem

    def _search_api_for_duplicates(self):
        logger.info('unable to determine if users exist through api')
        return []

    def determine_dependencies(self, candidates):
        self._dependencies = []

    def as_api_resources(self):
        return []

    def __repr__(self):
        return f'<{self.__class__.__name__}(filename={self.filename}, username={self.document["spec"]["username"]}>'
