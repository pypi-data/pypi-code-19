from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ConfigurationsConfig(AppConfig):

    name = 'configfactory.configurations'
    verbose_name = _("Configurations")
