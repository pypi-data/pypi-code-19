from gettext import gettext as _
import importlib
import re
import sys

from . import providers
from .exceptions import SocialError


# Helps to ensure that providers are safe module names.
provider_pattern = re.compile(r'^[a-z][a-z_]+[a-z]$')


# Only define error messages once.
exist_msg = _("The popular provider %s does not exist.")


class Manager(object):
    """Manages interactions with providers.

    This class is the developer's simplest interface with the social
    providers. It condenses things like credentials and calling
    providers by name.
    """

    def __init__(self, config):
        """Sets up the manager with configuration details for providers.

        The configuration should be a dict that looks like:
            {
                'facebook': {
                    'keys': 'that',
                    'are': 'used',
                    'by': 'facebook',
                },
                'google': {...},
            }

        This configuration also determines which providers will be made
        available through the manager, otherwise raising exceptions.

        Args:
            config: a dict representing all configured social providers.

        Raises:
            SocialError: The popular provider "%s" does not exist.
            ValueError: The popular configuration must be a dict.
        """
        if not isinstance(config, dict):
            raise ValueError(_(
                "The popular configuration must be a dict."
            ))
        self.providers = dict()
        for name in config:
            if not provider_pattern.match(name):
                raise SocialError(exist_msg % name)
            try:
                module = importlib.import_module(
                    ".%s" % name, providers.__name__
                )
            except ImportError:
                raise SocialError(exist_msg % name)
            try:
                provider = module.provider
            except AttributeError:
                raise SocialError(exist_msg % name)
            self.providers[name] = provider(config[name])

    def provider(self, name):
        """Returns the provider of choice.

        Args:
            name: a string name identifying the social provider.

        Returns:
            A subclass of popular.providers.base.Provider.

        Raises:
            SocialError: The popular provider "%s" does not exist.
        """
        try:
            return self.providers[name]
        except KeyError:
            raise SocialError(exist_msg % name)
