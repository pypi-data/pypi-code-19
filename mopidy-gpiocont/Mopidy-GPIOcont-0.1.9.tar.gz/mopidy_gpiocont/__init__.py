from __future__ import unicode_literals

import logging
import os

from mopidy import config, ext


__version__ = '0.1.9'

logger = logging.getLogger(__name__)


class Extension(ext.Extension):

    dist_name = 'Mopidy-GPIOcont'
    ext_name = 'gpiocont'
    version = __version__
    file1 = open("debug_init.txt", "w")

    def get_default_config(self):
        file1.write("default conf works")
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        file1.write(" config schema works")
        schema = super(Extension, self).get_config_schema()
        schema['play_pin'] = config.Integer()
        return schema

    def setup(self, registry):
        file1.write("setup works ")
        from .frontend import gpio_control
        registry.add('frontend', gpio_control)

    file1.close()
