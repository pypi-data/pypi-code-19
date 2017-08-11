import anyconfig
import os

from . import utils


class Reader():
    """Config Reader. Reads, validate and add default values to YAML"""

    def parse(self, config_file=None, specs=None, default_file=None):
        """Read a config_file, check the validity with a JSON Schema as specs
        and get default values from default_file if asked.

        All parameters are optionnal.

        If there is no config_file defined, read the venv base
        dir and try to get config/app.yml.

        If no specs, don't validate anything.

        If no default_file, don't merge with default values."""

        self._config_exists(config_file)
        self._specs_exists(specs)

        self.loaded_config = anyconfig.load(self.config_file, ac_parser='yaml')

        if default_file is not None:
            self._merge_default(default_file)

        if self.specs is None:
            return self.loaded_config

        self._validate()

        return self.loaded_config


    def _validate(self) -> None:
        (rc, err) = anyconfig.validate(self.loaded_config, anyconfig.load(self.specs, ac_parser='yaml'))

        if err != '':
            raise ValueError('Your config is not valid: {}'.format(err))


    def _config_exists(self, config_file: str) -> str:
        self.config_file = utils.get_venv_basedir() + '/config/app.yml'
        if config_file is not None:
            self.config_file = config_file

        if not os.path.isfile(self.config_file):
            raise IOError('Missing config file: "{}" does not exist'.format(self.config_file))


    def _merge_default(self, default_file: str) -> None:
        if not os.path.isfile(default_file):
            raise IOError("Your default ({}) does not exist".format(default_file))

        default_config = anyconfig.load(default_file)
        anyconfig.merge(default_config, self.loaded_config)

        self.loaded_config = default_config


    def _specs_exists(self, specs: str) -> None:
        self.specs = specs
        if self.specs is None:
            return

        # self.specs = os.path.abspath(os.path.dirname(__file__) + '/static/configspec.ini')
        if not os.path.isfile(self.specs):
            raise IOError("Your specs ({}) does not exist".format(self.specs))
