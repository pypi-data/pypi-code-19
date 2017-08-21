from django.template.response import SimpleTemplateResponse, TemplateResponse


def handle_exception(request, exc, template_name=None, status=None,
                     include_request=None, context=None):
    """
    This is djexcept's default exception handler.

    A django.template.response.SimpleTemplateResponse or
    django.template.response.TemplateResponse is returned.
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
