from __future__ import unicode_literals

import logging
import os

from mopidy import config, ext


__version__ = '0.1.20'

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
        return schema

    def get_command(self):
        from .commands import GPIOcontCommand
        return GPIOcontCommand()

    def validate_environment(self):
        # Any manual checks of the environment to fail early.
        # Dependencies described by setup.py are checked by Mopidy, so you
        # should not check their presence here.
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(4, GPIO.FALLING, callback=self.play, bouncetime=30)
        pass

    def setup(self, registry):
        logger.info("GPIOcont: Trying to ")
        from .frontend import GPIOcont
        registry.add('frontend', GPIOcont)
        logger.info("GPIOcont: setup done.")

    def play(self):
        logger.info(" MWUAHAHAHAH")
