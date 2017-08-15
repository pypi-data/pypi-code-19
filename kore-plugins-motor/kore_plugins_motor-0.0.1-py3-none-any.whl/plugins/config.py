import logging

from kore.components.plugins.base import BasePluginComponent

log = logging.getLogger(__name__)


class MotorPluginComponent(BasePluginComponent):

    def get_services(self):
        return (
            ('config', self.config),
        )

    def config(self, container):
        config = container('config')

        return config.get('motor', {})
