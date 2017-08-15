from gettext import gettext as _

from ..exceptions import SocialError
from ..utils import dict_to_query_string, uri_to_query_string_params


class Provider(object):
    """Base class for a social provider.

    Social providers are services like Facebook and Google who manage
    accounts for users. A Provider subclass will fill in the underlying
    functionality required to interact with those services.
    """

    # Configuration keys are each checked for on instantiation to let
    # the developer know what exactly is required.
    CONFIG_KEYS = []

    def __init__(self, config):
        """Does basic validation for the provider.

        This doesn't reach out to the actual service to validate
        anything, but rather it makes sure the proper ingredients and
        credentials are present.

        The required configuration details will change from provider to
        provider.

        Args:
            config: a dict containing credentials for a service provider
                application.

        Raises:
            SocialError: The %s provider requires the following
                keys: %s.
            TypeError: The "%s" must be a string.
            ValueError: The popular configuration for %s must be a
                dict.
        """
        assert self.CONFIG_KEYS
        self.name = self.__class__.__module__.split('.')[-1]
        if not isinstance(config, dict):
            raise ValueError(_(
                "The popular configuration for %s must be a dict."
            ) % self.name)
        if set(config.keys()) != set(self.CONFIG_KEYS):
            raise SocialError(
                _("The %s provider requires the following keys: %s.") % (
                    self.name,
                    ', '.join(self.CONFIG_KEYS),
                )
            )
        for name in config:
            if not isinstance(config[name], str):
                raise TypeError(_("The \"%s\" must be a string.") % name)
        self.config = config

    def get_auth_url(self, state):
        """Generates the url for the user to grant permission on.

        Args:
            state: a string of random characters to help prevent CSRF
                attacks.
            state: a string that was provided for this exact request
                when the user was first redirected.

        Returns:
            A string URL.
        """
        raise NotImplementedError()

    def get_user(self, uri, state):
        """Takes the response URI and retrieves a user from it.

        Args:
            uri: a string uri that the service sent the user to,
                including all query paramters attached.
            state: a string that was provided for this exact request
                when the user was first redirected.

        Returns:
            A popular.users.User instance.
        """
        raise NotImplementedError()

    def parse_uri(self, uri, required=None):
        """Parses the uri from the vendor.

        This will make sure the required parameters are present.

        Args:
            uri: a string URI.
            required: a list of parameter names.

        Returns:
            A dict of parsed query parameters.

        Raises:
            SocialError: Required query parameter \"%s\" is not
                present.
        """
        params = uri_to_query_string_params(uri)
        for param in required:
            if param not in params:
                raise SocialError(
                    _("Required query parameter \"%s\" is not present.") % param
                )
        return params

    def serialize_url(self, url, params):
        """Helper to add a query string to a url."""
        return '%s?%s' % (url, dict_to_query_string(params),)
