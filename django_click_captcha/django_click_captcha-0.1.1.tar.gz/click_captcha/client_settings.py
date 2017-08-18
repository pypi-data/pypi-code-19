from django.conf import settings

WIDGET_TEMPLATE = getattr(settings, "CLICK_CAPTCHA_WIDGET_TEMPLATE", False) or 'click_captcha/captcha.html'

TIMEOUT = getattr(settings, 'CLICK_CAPTCHA_TIMEOUT', 60)

# if not getattr(settings, 'CACHE_BACKEND', False):
#     setattr(settings, 'CACHE_BACKEND', "django.core.cache.backends.db.DatabaseCache")


