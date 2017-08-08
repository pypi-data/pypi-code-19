from __future__ import unicode_literals

import logging
import os

from mopidy import config, ext


__version__ = '0.2.2'

logger = logging.getLogger(__name__)



class Extension(ext.Extension):

    dist_name = 'Mopidy-GPIOcont'
    ext_name = 'gpiocont'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        logger.debug("GPIOcont: Default configuration loaded.")
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        # "Normal" control pins
        schema['enabled'] = config.Boolean()
        schema['play_pin'] = config.Integer(optional=True)
        schema['next_pin'] = config.Integer(optional=True)
        schema['prev_pin'] = config.Integer(optional=True)
        #Import A and B channels volume encoder
        schema['vol_a_pin'] = config.Integer(optional=True)
        schema['vol_b_pin'] = config.Integer(optional=True)
        schema['vol_bounce_time'] = config.Integer(optional=True)
        schema['vol_change'] = config.Integer(optional=True)
        #import dedicated playlist pins
        schema['list1_pin'] = config.Integer(optional=True)
        schema['list2_pin'] = config.Integer(optional=True)
        schema['list3_pin'] = config.Integer(optional=True)
        schema['list4_pin'] = config.Integer(optional=True)
        #import dedicated playlist names
        schema['list1_name'] = config.String()
        schema['list2_name'] = config.String()
        schema['list3_name'] = config.String()
        schema['list4_name'] = config.String()
        #imoport lcd address and port
        schema['lcd_enable'] = config.Boolean(optional=True)
        schema['lcd_address'] = config.String()
        schema['lcd_port'] = config.Integer(optional=True)
        logger.debug("GPIOcont: User specified configuration loaded.")
        return schema

    def get_command(self):
        from .commands import GPIOcontCommand
        return GPIOcontCommand()

    def validate_environment(self):
        # Any manual checks of the environment to fail early.
        # Dependencies described by setup.py are checked by Mopidy, so you
        # should not check their presence here.
        # if os.getuid() != 0:
        #     logger.warning("""GPIOcont: You are not root, change the line
        #     \"DAEMON_USER=mopidy\" to \"DAEMON_USER=root\"
        #     in the file \"/etc/init.d/mopidy\" if you are running Pi MusicBox.
        #     Else GPIO wont work""")
        # logger.debug("GPIOcont: Environment validated.")
        pass

    def setup(self, registry):
        from .frontend import GPIOcont
        registry.add('frontend', GPIOcont)

