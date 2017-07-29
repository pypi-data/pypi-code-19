# coding: utf-8
import sys

from django.db import models
from django.db.models import fields
from django.db.models.aggregates import Count
from django.db.models.expressions import Case, When, F, ExpressionWrapper
from django.db.models.functions import Now
from django.http.response import Http404
from django.utils import timezone

from djotali.core.models import TrackedModel, IntervalToSecondsNoSqlite


class Campaign(TrackedModel):
    name = models.CharField(max_length=200, unique=True)
    contacts_group = models.ForeignKey('contacts.ContactsGroup')
    start_date = models.DateTimeField()
    message = models.TextField(max_length=200)

    def count_sent(self):
        return self.count_by_status(1)

    def count_unsent(self):
        return self.count_by_status(0)

    def count_failed(self):
        return self.count_by_status(-1)

    def is_started(self):
        return self.start_date <= timezone.now()

    def is_opened(self):
        return self.is_started()

    def count_by_status(self, status):
        return self.notifications.filter(status=status).count()

    def count_sent_percent(self):
        return 100 * self.count_sent() / self.notifications.count()

    def count_pending(self):
        return self.notifications.count() - self.count_sent()

    def __str__(self):
        return self.name

    @staticmethod
    def get_closest_campaigns_query_set():
        # We order the campaigns as following:
        # The valid campaigns (start date is after NOW) appears first
        # Then we display the invalid campaigns (start date is before NOW)
        # The closest valid campaigns are displayed first
        # The closest invalid campaigns are displayed then
        #
        # To implement that behaviour we first need to compute the delta between now and the start date
        # If that delta is negative, campaign is valid as it means that NOW is lesser than start date
        # If that delta is positive, campaign is invalid as it means that NOW is greater than start date
        #
        # Then we compute from the delta a proximity order key to represent the "closest" notion
        #
        # "Closest" valid campaigns are those with the numerically greater negative deltas
        # To make them appear first, we need to reverse that order
        # So we subtract them from the lowest possible integer to get the proximity order
        # By doing that, the greatest negative deltas become the lowest proximity order
        # For example, if there are 2 valid campaigns with deltas -2 and -1, -1 is the closest campaign
        # If we make proximity order directly equal to deltas, -2 will appear first as -2 < -1
        # But if for example -10 was the lowest integer, when subtracting it the deltas (-10 - delta)
        # We respectively get for -2 and -1 campaigns, -8 and -9 as proximity order
        # The valid campaign with -1 delta will then be displayed first as -9 < -8
        #
        # "Closest" invalid campaigns are those with the numerically lower positive deltas
        # In this case no need to reverse the order so the proximity key can directly be equal to delta
        # For example, if there are 2 invalid campaigns with deltas 2 and 1, 1 is the closest campaign
        # If proximity order is equal to delta, it will respectively be equal to 2 and 1
        # 1 < 2 so "1" campaign will appear before "2" campaign
        #
        # This is the behaviour explained above that is implemented in this SQL query
        # The whole computation occurs in DB to speed it up and benefits from native pagination
        return Campaign.objects.annotate(
            notification_count=Count('notifications'),
            sent_count=models.Sum(
                models.Case(
                    models.When(notifications__status=Notification.SENT, then=1),
                    default=0, output_field=models.IntegerField()
                )
            ),
            failed_count=models.Sum(
                models.Case(
                    models.When(notifications__status=Notification.FAILED, then=1),
                    default=0, output_field=models.IntegerField()
                )
            ),
            delta_now=ExpressionWrapper(IntervalToSecondsNoSqlite(Now() - F('start_date')), output_field=fields.IntegerField()),
            start_date_proximity_order_key=Case(
                When(delta_now__gt=0, then=F('delta_now')),
                When(delta_now__lte=0, then=ExpressionWrapper((-sys.maxsize - 1) - F('delta_now'), output_field=fields.IntegerField())),
                output_field=fields.IntegerField(),
            ),
        ).order_by('start_date_proximity_order_key')


class Notification(TrackedModel):
    FAILED = -1
    PROGRESS = 0
    SENT = 1
    STATUSES = (
        (FAILED, 'Failed'),
        (PROGRESS, 'Progress'),
        (SENT, 'Sent'),
    )
    campaign = models.ForeignKey('Campaign', related_name='notifications', on_delete=models.CASCADE)
    contact = models.ForeignKey('contacts.Contact')
    status = models.SmallIntegerField(
        choices=STATUSES, default=PROGRESS)
    send_date = models.DateTimeField(null=True, blank=True)

    def sent(self):
        self.send_date = timezone.now()
        self.status = self.SENT

    def failed(self):
        self.status = self.FAILED

    def is_sent(self):
        return self.status == self.SENT

    def sendable(self):
        return not self.contact.is_removed and self.status == self.PROGRESS

    @classmethod
    def tag_as_sent(cls, notification_id):
        notification = Notification.objects.get(pk=notification_id)
        notification.sent()
        notification.save()

    @classmethod
    def tag_as_failed(cls, notification_id):
        notification = Notification.objects.get(pk=notification_id)
        notification.failed()
        notification.save()

    @classmethod
    def get_status_value(cls, status):
        if not hasattr(Notification, status):
            raise Http404('"{}" is an unknown status'.format(status))
        return getattr(Notification, status)

    class Meta:
        unique_together = ('campaign', 'contact')
        ordering = ['status']
