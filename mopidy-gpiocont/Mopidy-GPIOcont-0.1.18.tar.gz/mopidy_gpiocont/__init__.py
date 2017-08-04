from __future__ import unicode_literals

import logging
import os

from mopidy import config, ext


__version__ = '0.1.18'

logger = logging.getLogger(__name__)



class Extension(ext.Extension):

    dist_name = 'Mopidy-GPIOcont'
    ext_name = 'gpiocont'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        logger.info("GPIOcont: Default configuration loaded.")
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['play_pin'] = config.Integer()
        logger.info("GPIOcont: User specified configuration loaded.")
        logger.info("pins= " + schema)
        return schema

    def setup(self, registry):
        logger.info("GPIOcont: Trying to ")
        from .frontend import GPIOcont
        registry.add('frontend', GPIOcont)
        logger.info("GPIOcont: setup done.")


