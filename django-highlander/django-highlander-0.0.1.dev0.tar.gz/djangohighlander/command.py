from django.core.management.base import BaseCommand
from tendo import singleton
import hashlib


class Highlander(BaseCommand):
    def execute(self, *args, **options):
        me = singleton.SingleInstance()
        super(Highlander, self).execute(*args, **options)

