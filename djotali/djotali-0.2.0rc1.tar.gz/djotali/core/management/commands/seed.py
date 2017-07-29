# coding: utf-8
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from djotali.campaigns.models import Campaign
from djotali.contacts.models import Contact, ContactsGroup
from djotali.core.seed.factories import ContactsGroupFactory, CampaignFactory


class Command(BaseCommand):
    help = 'Seed Database'

    def handle(self, *args, **options):
        with transaction.atomic():
            try:
                # Drop All first
                self.stdout.write(self.style.WARNING('Truncating tables first...'))
                ContactsGroup.user_contacts_groups.all().delete()
                Contact.objects.all().delete()
                Campaign.objects.all().delete()

                ContactsGroupFactory.create_batch(3)
                all_contacts = ContactsGroup.objects.get(name=ContactsGroup.all_contacts)
                all_contacts.contacts = Contact.objects.all()
                all_contacts.save()
                CampaignFactory.create_batch(5)
                self.stdout.write(self.style.SUCCESS('Database seeded'))
            except CommandError as e:
                self.stdout.write(self.style.ERROR('Failed to seed database. Rolling back transaction', e))
