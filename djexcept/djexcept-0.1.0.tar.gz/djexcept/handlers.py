from django.template.response import SimpleTemplateResponse, TemplateResponse


def handle_exception(request, exc, template_name=None, status=None,
                     include_request=None, context=None):
    """
    This is djexcept's default exception handler.

    It accepts the following optional keyword arguments:
        * template_name: name of the template to use
        * status: HTTP status code
        * include_request: whether to include the request in template
          context
        * context: dictionary of which a copy is used as starting point
          for the template context; values in that context won't be
          overwritten

    A django.template.response.SimpleTemplateResponse is returned.
    """

    # initialize context if needed and shallow-copy it afterwards
    context = dict(context or {})

    context.setdefault("exc", exc)
    context.setdefault("exc_name", exc.__class__.__name__)
    context.setdefault("exc_module", exc.__class__.__module__)
    context.setdefault("exc_modname", "{}.{}".format(
            exc.__class__.__module__, exc.__class__.__name__))
    context.setdefault("status", status)

    if include_request:
        return TemplateResponse(request, template_name, context=context,
                                status=status)
    else:
        return SimpleTemplateResponse(template_name, context=context,
                                      status=status)
