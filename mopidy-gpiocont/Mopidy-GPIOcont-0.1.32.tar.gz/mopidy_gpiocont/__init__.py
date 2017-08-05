from __future__ import unicode_literals

import logging
import os

from mopidy import config, ext


__version__ = '0.1.32'

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
        schema['enabled'] = config.Boolean()
        schema['play_pin'] = config.Integer()
        logger.debug("GPIOcont: User specified configuration loaded.")
        return schema

    def get_command(self):
        from .commands import GPIOcontCommand
        logger.debug("GPIOcont: get_commants done")
        return GPIOcontCommand()

    def validate_environment(self):
        # Any manual checks of the environment to fail early.
        # Dependencies described by setup.py are checked by Mopidy, so you
        # should not check their presence here.
        if os.getuid() != 0:
            logger.warning("""GPIOcont: You are not root, change the line
            \"DAEMON_USER=mopidy\" to \"DAEMON_USER=root\"
            in the file \"/etc/init.d/mopidy\" if you are running Pi MusicBox.
            Else GPIO wont work""")
        logger.debug("GPIOcont: Environment validated.")
        pass

    def setup(self, registry):
        from .frontend import GPIOcont
        registry.add('frontend', GPIOcont)

