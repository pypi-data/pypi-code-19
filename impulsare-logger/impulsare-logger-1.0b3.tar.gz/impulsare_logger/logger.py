import logging
import os

from impulsare_config import Reader, utils
from logging.handlers import RotatingFileHandler


class Logger():
    """Config Reader. Reads, validate and add default values to YAML"""

    def __init__(self, app: str, config_file: str = None):
        """Write logs to a file, with the app's name"""

        base_path = os.path.abspath(os.path.dirname(__file__))
        config_specs = base_path + '/static/specs.yml'
        config_default = base_path + '/static/default.yml'

        self.config = Reader().parse(config_file, config_specs, config_default).get('logger')

        self.app = app

        self.level = getattr(logging, self.config.get('level'))
        self.log = logging.getLogger(app)
        self.log.setLevel(self.level)

        if self.log.hasHandlers():
            return

        if self.config.get('handlers')['file'] is True:
            self.filename = self._get_filename()
            self.log.addHandler(self._get_file_handler())
        if self.config.get('handlers')['console'] is True:
            self.log.addHandler(self._get_stream_handler())


    def _get_filename(self):
        directory = self.config.get('directory')
        if directory is None:
            return utils.get_venv_basedir() + '/logs/{}.log'.format(self.app)

        return '{}/{}.log'.format(directory, self.app)


    def _get_file_handler(self):
        max_size = int(self.config.get('max_size') * 1024 * 1024)
        rotate = int(self.config.get('rotate'))

        try:
            file_handler = RotatingFileHandler(self.filename, 'a', max_size, rotate)
            file_handler.setLevel(self.level)
            file_handler.setFormatter(logging.Formatter(self.config.get('formatter')))
        except Exception:
            raise IOError("Can't write to '{}'".format(self.filename))

        return file_handler


    def _get_stream_handler(self):
        from click import style

        log_format = style('[LOGGER] ', fg='green')
        log_format += style('(' + self.app.upper() + ') ', fg='yellow')
        log_format += '%(levelname)s - %(message)s'

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(self.level)
        stream_handler.setFormatter(logging.Formatter(log_format))

        return stream_handler
