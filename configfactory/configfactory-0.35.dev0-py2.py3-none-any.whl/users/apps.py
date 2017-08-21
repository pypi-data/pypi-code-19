from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import ugettext_lazy as _

from configfactory.users.management import create_default_users


class UsersConfig(AppConfig):

    name = 'configfactory.users'
    verbose_name = _("Users")

    def ready(self):
        post_migrate.connect(create_default_users, sender=self)
