# coding: utf-8
"""
Django-rest-easy provides base classes for API views and serializers.

To leverage the QOL features of django-rest-easy, you should use the followint base classes for your serializers:
* :class:`rest_easy.serializers.Serializer`
* :class:`rest_easy.serializers.ModelSerializer`

And if it's model-based, it should use one of the base views provided in the :mod:`rest_easy.views`
module - preferably :class:`rest_easy.views.ModelViewSet` or :class:`rest_easy.views.ReadOnlyModelViewSet`.

As a baseline, all responses using django-rest-easy extension will contain top-level model and schema fields.

Guidelines regarding schemas are as usual: they have to be 100% backwards compatible. In the case of breaking changes,
a serializer with new schema should be created, and the old one slowly faded away - and removed only when no
applications use it - or when it's decided that the feature can't be supported anymore.

An alternative to multi-version fadeout is single-version fadeout, where the change is implemented as a set of
acceptable changes (that is, you can remove the old field only when all clients stop using it - even if it means
sending duplicate data for quite some time).

The classes from this module don't disable any behaviour inherent to Django Rest Framework - anything that is possible
there will be possible with the django-rest-easy base classes.

Uses followint settings:
REST_EASY_AUTOIMPORT_SERIALIZERS_FROM - for autoimporting serializers.
REST_EASY_VIEW_BASES - for prepending bases to generic views.
"""
from django.apps import AppConfig
from django.conf import settings

default_app_config = 'rest_easy.ApiConfig'


class ApiConfig(AppConfig):
    """
    AppConfig autoimporting serializers.

    It scans all installed applications for modules specified in settings.REST_EASY_AUTOIMPORT_SERIALIZERS_FROM
    parameter, trying to import them so that all residing serializers using
    :class:`rest_easy.serializers.SerializerCreator` metaclass will be added to
    :class:`rest_easy.registers.SerializerRegister`.

    In the case of a module not being present in app's context, the import is skipped.
    In the case of a module existing but failing to import, an exception will be raised.
    """
    name = 'rest_easy'
    label = 'rest_easy'

    default_paths = ['serializers', 'api.serializers']

    @property
    def paths(self):
        """
        Get import paths - from settings or defaults.
        """
        return getattr(settings, 'REST_EASY_AUTOIMPORT_SERIALIZERS_FROM', self.default_paths)

    def autodiscover(self):
        """
        Auto-discover serializers in installed apps, fail silently when not present, re-raise exception when present
        and import fails. Borrowed form django.contrib.admin with added nested presence check.
        """

        from importlib import import_module
        from django.utils.module_loading import module_has_submodule

        for app in settings.INSTALLED_APPS:
            mod = import_module(app)

            # Attempt to import the app's serializers.
            for item in self.paths:
                try:
                    import_module('{}.{}'.format(app, item))

                except (TypeError, ImportError):
                    # Decide whether to bubble up this error. If the app just
                    # doesn't have serializers module, we can ignore the error
                    # attempting to import it, otherwise we want it to bubble up.
                    curr = mod
                    curr_path = app
                    for part in item.split('.'):
                        if not module_has_submodule(curr, part):
                            break
                        curr_path += '.' + part
                        curr = import_module(curr_path)
                    else:
                        raise

    def ready(self):
        self.autodiscover()
