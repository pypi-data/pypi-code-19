from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import ugettext_lazy as _

from configfactory.environments.management import create_environments


class EnvironmentsConfig(AppConfig):

    name = 'configfactory.environments'
    verbose_name = _("Environments")

    def ready(self):
        post_migrate.connect(create_environments, sender=self)
