import base64

import qrcode
from django.http import HttpResponse


def qrcode_img_view(request, b64code):
    content = base64.urlsafe_b64decode(b64code.encode())
    resp = HttpResponse(content_type="image/png")
    img = qrcode.make(content)
    img.save(resp)
    return resp
