try:
    import django.conf
    assert django.conf.settings.configured
except (ImportError, AssertionError):
    # django is not available, hence no functionality is provided.
    pass
else:
    from .registration import (
            register, unregister, is_registered
        )


__version__ = "0.1.0"
