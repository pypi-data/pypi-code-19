# coding: utf-8
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Send Notification'

    def add_arguments(self, parser):
        parser.add_argument('notification_id', nargs='+', type=int)

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS("Notification {}".format(options['notification_id'])))
        except CommandError as e:
            self.stdout.write(self.style.ERROR("Error : {}".format(e)))
