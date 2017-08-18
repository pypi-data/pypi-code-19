from io import BytesIO
from django.conf import settings
from django.core.cache import cache
from django.http.response import HttpResponse, Http404
from django.views.generic import View
from click_captcha.image_unicode import ImageChar


class CaptchaView(View):
    def get(self, request, *args, **kwargs):
        if not kwargs.get('uuid', None) or len(kwargs['uuid']) > 250:
            raise Http404()
        width = 30
        height = 50
        ic = ImageChar(char_number=7, font_size=width, height=height)
        point_list, code_img = ic.random_chinese()
        cache.set(kwargs['uuid'], [point_list, width, height], settings.CLICK_CAPTCHA_TIMEOUT)
        byte_io = BytesIO()
        code_img.save(byte_io, 'PNG', quality=70)
        byte_io.seek(0)

        return HttpResponse(content=byte_io.read(), content_type='image/png')
