from __future__ import unicode_literals

import logging
import os

from mopidy import config, ext


__version__ = '0.1.11'

logger = logging.getLogger(__name__)

LOG_FILENAME = 'logging_example.out'
logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.DEBUG,
                    )

logging.debug('This message should go to the log file')


class Extension(ext.Extension):

    dist_name = 'Mopidy-GPIOcont'
    ext_name = 'gpiocont'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        logging.error("heehooohallooo")
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['play_pin'] = config.Integer()
        return schema

    def setup(self, registry):
        logger.error("setup done")
        logging.debug("debug setup done")
        from .frontend import gpio_control
        registry.add('frontend', gpio_control)


