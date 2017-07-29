# coding: utf-8
import datetime
import random

import factory
from django.db.models import signals
from django.utils import timezone
from faker import Faker

import djotali.campaigns.models as campaigns_models
import djotali.contacts.models as contacts_models

faker = Faker('fr_FR')


class CampaignFactory(factory.DjangoModelFactory):
    class Meta:
        model = campaigns_models.Campaign

    message = factory.Faker('text', max_nb_chars=140)

    @factory.lazy_attribute
    def name(self):
        return "{}% Off ! {}".format(
            factory.Faker('random_int', min=20, max=85).generate({}),
            factory.Faker('sentence', nb_words=2).generate({})
        )

    @factory.lazy_attribute
    def start_date(self):
        return timezone.now() + random.choice([-2, 2]) * datetime.timedelta(days=random.choice(range(0, 10)))

    contacts_group = factory.Iterator(contacts_models.ContactsGroup.objects.all())

    @factory.post_generation
    def make_notifications(self, create, extracted, **kwargs):
        if not create:
            return

        if self.contacts_group.contacts:
            for contact in self.contacts_group.contacts.all():
                n = NotificationFactory.create(contact=contact, campaign=self, status=0)
                self.notifications.add(n)


class ContactsGroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = contacts_models.ContactsGroup

    name = factory.Faker('company')
    # TODO Do a mix
    is_removed = False

    @factory.post_generation
    def contacts(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        contacts = ContactFactory.create_batch(20)
        # A list of groups were passed in, use them
        for contact in contacts:
            if not contact.is_removed:
                self.contacts.add(contact)


@factory.django.mute_signals(signals.pre_save, signals.post_save)
class ContactFactory(factory.DjangoModelFactory):
    class Meta:
        model = contacts_models.Contact

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    phone_number = factory.Faker('senegal_phone_number')
    # TODO Do a mix
    is_removed = False


class NotificationFactory(factory.DjangoModelFactory):
    class Meta:
        model = campaigns_models.Notification

    campaign = factory.Iterator(campaigns_models.Campaign.objects.all())
    contact = factory.Iterator(contacts_models.Contact.objects.all())
    status = random.choice([0, 1, -1])
