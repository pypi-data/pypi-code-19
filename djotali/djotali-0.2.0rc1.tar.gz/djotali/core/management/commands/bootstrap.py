from django.core.management import BaseCommand

from djotali.contacts.models import ContactsGroup


class Command(BaseCommand):
    help = 'Bootstrap application'

    def handle(self, *args, **options):
        if not ContactsGroup.objects.filter(name=ContactsGroup.all_contacts).exists():
            ContactsGroup.objects.bulk_create([
                ContactsGroup(name=ContactsGroup.all_contacts),
            ])
            self.stdout.write(self.style.SUCCESS('Created all contacts group.'))
        else:
            self.stdout.write(self.style.SUCCESS('All contacts group already exists.'))
