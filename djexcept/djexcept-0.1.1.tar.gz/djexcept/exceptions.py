from django.core.exceptions import ImproperlyConfigured as _ImproperlyConfigured


class ImproperlyConfigured(_ImproperlyConfigured):
    """
    Is raised when something went wrong at settings parsing.
    """
    pass

class RegistrationError(Exception):
    """
    Is raised when an illegal call to register() or unregister() is made.
    """
    pass
