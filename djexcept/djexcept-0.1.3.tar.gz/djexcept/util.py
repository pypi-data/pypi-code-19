def populate_context(context, exc, status=None):
    """
    Populates the given context dictionary with djexcept's handy default
    values. The dictionary is altered in-place, but values that are
    already present won't be overwritten.

    The following values are added to the context:
        * exc: the exception object
        * exc_name: the name of the exception type
          (e.g. PermissionDenied or ValueError)
        * exc_module: the module name of the exception's type
          (e.g. django.core.exceptions or builtins)
        * exc_modname: both concatenated, separated by a period
          (e.g. django.core.exceptions.PermissionDenied or
          builtins.ValueError)
        * status: the HTTP status code used (only added if not None)
    """

    context.setdefault("exc", exc)
    context.setdefault("exc_name", exc.__class__.__name__)
    context.setdefault("exc_module", exc.__class__.__module__)
    context.setdefault("exc_modname", "{}.{}".format(
            exc.__class__.__module__, exc.__class__.__name__))

    if status is not None:
        context.setdefault("status", status)
