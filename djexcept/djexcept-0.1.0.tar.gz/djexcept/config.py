from django.conf import settings

from importlib import import_module

from .exceptions import ImproperlyConfigured
from .handlers import handle_exception


class Config:
    """
    Parses djexcept-specific settings from django.conf.settings, sets
    default values and holds them for use by other components.
    """

    def __init__(self):
        self.handle_subclasses = getattr(
                settings, "DJEXCEPT_HANDLE_SUBCLASSES", True)
        self.disable_on_debug = getattr(
                settings, "DJEXCEPT_DISABLE_ON_DEBUG", False)

        self.default_handler_kwargs = {
            "template_name": getattr(
                settings, "DJEXCEPT_TEMPLATE_NAME", "exception.html"),
            "status": getattr(settings, "DJEXCEPT_STATUS", 400),
            "include_request": getattr(settings, "DJEXCEPT_INCLUDE_REQUEST",
                True),
        }

        try:
            handler_name = getattr(
                    settings, "DJEXCEPT_DEFAULT_EXCEPTION_HANDLER")
        except AttributeError:
            # use default handler
            handler = handle_exception
        else:
            handler = load_exception_handler(handler_name)
        self.default_handler = handler


def load_exception_handler(handler_name):
    mod_path, _, func_name = handler_name.rpartition(".")
    if not mod_path:
        raise ImproperlyConfigured(
                "{} is not a valid exception handler".format(handler_name))
    module = import_module(mod_path)
    return getattr(module, func_name)


# config should be initialized once.
config = Config()
