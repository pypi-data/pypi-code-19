from kore.components.plugins.base import BasePluginComponent

import ptvsd


class PtvsdPlugin(BasePluginComponent):

    def get_services(self):
        return (
            ('config', self.config),
        )

    def config(self, container):
        config = container('config')

        return config.get('ptvsd', {})

    def post_hook(self, container):
        config = container('kore.components.ptvsd.config')

        secret = config.get('secret', 'my_secret')
        host = config.get('host', '0.0.0.0')
        port = config.get('port', '3000')

        ptvsd.enable_attach(secret, address=(host, int(port)))
