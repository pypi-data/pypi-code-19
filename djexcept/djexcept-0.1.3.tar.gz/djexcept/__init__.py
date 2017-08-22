try:
    from django.conf import settings as _django_settings
    assert _django_settings.configured
except (ImportError, AssertionError):
    # django is not available or still unconfigured, hence no
    # functionality is provided.
    pass
else:
    from .registration import (
            register, unregister, is_registered, is_handled
        )


__version__ = "0.1.3"
