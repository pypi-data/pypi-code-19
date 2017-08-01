import base64

import qrcode
from django import template
from django.urls import reverse
from django.utils.encoding import force_bytes

from qrcode2.utils import img_to_base64_data

register = template.Library()


@register.filter
def qrcode_src(text):
    try:
        return reverse('qrcode', args=(base64.b64encode(force_bytes(text)),))
    except Exception as e:
        img = qrcode.make(str(text))
        return img_to_base64_data(img)
