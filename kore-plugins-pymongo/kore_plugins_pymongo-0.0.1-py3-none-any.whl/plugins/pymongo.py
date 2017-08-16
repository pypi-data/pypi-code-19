from kore.components.plugins.base import BasePluginComponent

from pymongo import MongoClient


class PymongoPlugin(BasePluginComponent):

    def get_services(self):
        return (
            ('config', self.config),
            ('client', self.client),
        )

    def config(self, container):
        config = container('config')

        return config.get('pymongo', {})

    def client(self, container):
        config = container('kore.components.pymongo.config')

        return MongoClient(config['url'])
