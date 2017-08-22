import inspect

from .config import config, load_exception_handler
from .exceptions import RegistrationError


_registered_exception_classes = {}


def register(exc_cls=None, **attrs):
    """
    Registers the given Exception subclass for error handling with
    djexcept.

    The additional keyword arguments are treated as follows:
        * handler: an exception handler to ovewrite the
          DJEXCEPT_EXCEPTION_HANDLER setting
        * handle_subtypes: may be used to overwrite the
          DJEXCEPT_HANDLE_SUBTYPES setting on a per exception basis

    All other keyword arguments are passed directly to the handler
    function when there is an exception to handle. See documentation
    for their meanings.

    This function may also be used as a class decorator when defining
    custom exceptions.

    djexcept.exceptions.RegistrationError is raised if the class was
    already registered.
    """

    def register(exc_cls):
        if not issubclass(exc_cls, Exception):
            raise RegistrationError(
                    "{} is not a subclass of Exception".format(exc_cls))
        if is_registered(exc_cls):
            raise RegistrationError(
                    "{} is already registered with djexcept.".format(exc_cls))
        if isinstance(attrs.get("handler"), str):
            # lazy-import the handler
            attrs["handler"] = load_exception_handler(attrs["handler"])
        _registered_exception_classes[exc_cls] = attrs
        return exc_cls

    # Return a class decorator if class is not given
    if exc_cls is None:
        return register
    # Register the class
    return register(exc_cls)

def unregister(exc_cls):
    """
    Unregisters the given exception class from djexcept.

    djexcept.exceptions.RegistrationError is raised if the class wasn't
    registered.
    """
    try:
        del _registered_exception_classes[exc_cls]
    except KeyError:
        raise RegistrationError(
                "{} is not registered with djexcept.".format(exc_cls))

def is_registered(exc_cls):
    """
    Checks whether the given Exception subclass is registered for use
    with djexcept.
    """

    return exc_cls in _registered_exception_classes

def is_handled(exc_cls):
    """
    Checks whether the given exception class is handled by djexcept.
    If DJEXCEPT_HANDLE_SUBTYPES setting is disabled and not overwritten
    at registration stage, this function returns the same result as
    djexcept.is_registered().
    """

    for cls, attrs in _registered_exception_classes.items():
        # require exact match if include_subclasses is disabled
        if not attrs.get("handle_subtypes", config.handle_subtypes) \
           and cls is not exc_cls:
            continue
        if issubclass(exc_cls, cls):
            return True
    return False


def _get_best_exception_class_match(exc_cls):
    """
    Searches the closest registered ancestor of the given exception
    class and returns it or None, if none exists. handle_subtypes
    attributes are considered.
    """

    mro = inspect.getmro(exc_cls)
    best = None
    for cls, attrs in _registered_exception_classes.items():
        # require exact match if include_subclasses is disabled
        if not attrs.get("handle_subtypes", config.handle_subtypes) and \
           cls is not exc_cls:
            continue
        if cls in mro:
            idx = mro.index(cls)
            if best is None or idx < best_idx:
                best = cls
                best_idx = idx
    return best

def _get_exception_handler_attrs(exc_cls, exact=False):
    """
    Return the attributes provided when the given class was registered
    or None, if it isn't registered at all.

    If exact is set to True, all settings of handle_subtypes are ignored
    and only an exact match in the registration database will be
    considered valid.
    """

    if not exact:
        exc_cls = _get_best_exception_class_match(exc_cls)

    return _registered_exception_classes.get(exc_cls)

