import logging

from motor.motor_asyncio import AsyncIOMotorClient

from kore.components.plugins.base import BasePluginComponent

log = logging.getLogger(__name__)


class AsyncioMotorPluginComponent(BasePluginComponent):

    def get_services(self):
        return (
            ('client', self.client),
        )

    def client(self, container):
        config = container('kore.components.motor.config')

        url = config.get('url', 'localhost')
        timeout = config.get('timeout', 1)

        return AsyncIOMotorClient(url, serverSelectionTimeoutMS=timeout)
