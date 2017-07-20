# coding: utf-8
from django.conf import settings

try:
    from storages.backends.s3boto import S3BotoStorage

    from .hashed import (
        HashedStorageMixin,
        CachedHashValueFilesMixin,
        CachedManifestFilesMixin
    )
    from .overwrite import OverwriteStorageMixin, IgnoreDeleteStorageMixin

    class PrivateS3StorageMixin(object):
        default_acl = "private"
        querystring_auth = True
        custom_domain = None
        encryption = True
        location = getattr(settings, 'PRIVATE_MEDIAFILES_LOCATION',
                           '{}/{}'.format(getattr(settings, 'PROJECT_NAME', 'django'), 'private-media'))

    class ApiOnlyS3StorageMixin(PrivateS3StorageMixin):
        querystring_auth = False

    class StaticS3Storage(CachedHashValueFilesMixin, OverwriteStorageMixin,
                          IgnoreDeleteStorageMixin, S3BotoStorage):
        location = getattr(settings, 'STATICFILES_LOCATION',
                           '{}/{}'.format(getattr(settings, 'PROJECT_NAME', 'django'), 'static'))

    class ManifestFilesStaticS3Storage(CachedManifestFilesMixin, OverwriteStorageMixin,
                                       IgnoreDeleteStorageMixin, S3BotoStorage):
        location = getattr(settings, 'STATICFILES_LOCATION',
                           '{}/{}'.format(getattr(settings, 'PROJECT_NAME', 'django'), 'static'))

    class MediaS3Storage(S3BotoStorage):
        location = getattr(settings, 'MEDIAFILES_LOCATION',
                           '{}/{}'.format(getattr(settings, 'PROJECT_NAME', 'django'), 'media'))

    class HashedMediaS3Storage(HashedStorageMixin, OverwriteStorageMixin, MediaS3Storage):
        IGNORE_OVERWRITE = True

    class PrivateMediaS3Storage(PrivateS3StorageMixin, MediaS3Storage):
        pass

    class PrivateHashedMediaS3Storage(PrivateS3StorageMixin, HashedMediaS3Storage):
        pass

    class ApiOnlyMediaS3Storage(ApiOnlyS3StorageMixin, MediaS3Storage):
        pass

    class ApiOnlyHashedMediaS3Storage(ApiOnlyS3StorageMixin, HashedMediaS3Storage):
        pass

except ImportError:  # pragma: no cover
    pass
