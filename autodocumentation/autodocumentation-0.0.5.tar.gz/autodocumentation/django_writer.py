import json

from autodocumentation.decorator import autodoc
from autodocumentation.flask_writer import BaseWriter
try:
    from rest_framework.request import Request
except:
    pass

class DjangoWriter(BaseWriter):

    def serialize(self, func, output, *a, **k):

        request = a[0] if isinstance(a[0], Request) else a[1]

        if hasattr(request, "_request"):
            request = request._request

        return dict(
            method=request.method,
            url=request.get_full_path(),
            body=json.dumps({
                key: value[0]
                for key, value in request.POST.items()
            }, indent=4, sort_keys=True),
            headers=json.dumps({
                key:value
                for key, value in request.META.items()
                if key.startswith("HTTP_")
            }, indent=4, sort_keys=True),
            response=json.dumps(
                output.data,
                indent=4, sort_keys=True
            ),
            **autodoc.get_context()
        )

