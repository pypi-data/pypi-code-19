from django.db import models
from django.urls import reverse

from staff.behaviors import WhiteLabelClientMixin, TimeStampedMixin

from .constants import REQUEST_STATUSES, STATUS_OPEN
from .managers import JobRequestQuerySet


class JobRequest(WhiteLabelClientMixin):
    """
    Request to do a Job created by a User towards a general.
    """
    owner = models.ForeignKey('staff.Member')
    title = models.CharField(max_length=254)
    slug = models.SlugField(primary_key=True)
    description = models.TextField()
    status = models.SmallIntegerField(choices=REQUEST_STATUSES, default=STATUS_OPEN)
    deadline = models.DateField(null=True, blank=True)
    location = models.ForeignKey('trade.RequestLocation', related_name='+', null=True, blank=True,
                                 on_delete=models.SET_NULL)
    job = models.OneToOneField('jobs.Job', related_name='job_request', null=True, blank=True,
                               on_delete=models.SET_NULL)

    objects = JobRequestQuerySet.as_manager()

    def __str__(self):
        return '%s (%s)' % (self.title[:50], self.owner)

    def get_absolute_url(self):
        return reverse('trade:listview', args=(self.slug,))

    @property
    def to_be_processed(self):
        return self.status == STATUS_OPEN


class JobApplication(TimeStampedMixin):
    """
    Application to `JobRequest` created by a WhiteLabelClient-user.
    """
    job_request = models.ForeignKey('trade.JobRequest')
    job = models.ForeignKey('jobs.Job', null=True, blank=True)
    owner = models.ForeignKey('staff.Member')


class RequestLocation(TimeStampedMixin):
    """
    Physical location related to `JobRequest`.
    """
    name = models.CharField(max_length=512)
    address = models.CharField(max_length=512)
    postal_code = models.CharField(max_length=512, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    city = models.CharField(max_length=512, blank=True)
    note = models.CharField(max_length=512, blank=True)

    def __str__(self):
        return '%s, %s' % (self.address, self.city)


class TradeComment(TimeStampedMixin):
    """
    This Comment objects is used for Trade models only.
    """
    created_by = models.ForeignKey('staff.Member')
    text = models.TextField()

    # Objects to point to
    request = models.ForeignKey('trade.JobRequest', related_name='comments',
                                on_delete=models.CASCADE)

    def __str__(self):
        return '%s, %s' % (self.text[:50], self.created_by)

    def get_absolute_url(self):
        if self.job:
            return self.job.get_absolute_url()
