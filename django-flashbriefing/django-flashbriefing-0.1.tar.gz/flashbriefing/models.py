import uuid

from django.db import models
from django.utils import timezone

try:
    from django.urls import reverse
except ImportError:
    # for compatibility with Django 1.9 and 1.8
    from django.core.urlresolvers import reverse


def audio_upload_path(instance, filename):
    name, ext = filename.rsplit('.', 1)
    return 'flashbriefing/{}/{}.{}'.format(
        instance.feed.uuid, instance.uuid, ext)


def new_uuid():
    return uuid.uuid4().hex


class Feed(models.Model):
    title = models.CharField(max_length=128)
    uuid = models.CharField(max_length=32, default=new_uuid)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('flashbriefing:feed', args=[self.uuid, 'json'])

    def published_items(self):
        now = timezone.now()
        return self.items.filter(
            published_date__lte=now, is_published=True)[:5]


class Item(models.Model):

    TYPE_AUDIO = 'audio'
    TYPE_TEXT = 'text'

    ITEM_TYPE_CHOICES = (
        (TYPE_AUDIO, 'Audio'),
        (TYPE_TEXT, 'Text'),
    )

    feed = models.ForeignKey(Feed, related_name='items')
    uuid = models.CharField(max_length=32, default=new_uuid)
    item_type = models.CharField(
        max_length=16, choices=ITEM_TYPE_CHOICES, blank=True)
    title = models.CharField(max_length=255)
    published_date = models.DateTimeField()
    is_published = models.BooleanField(default=True)
    audio_content = models.FileField(
        blank=True, upload_to=audio_upload_path,
        help_text='The audio content should be 256kbps mono or stereo MP3.')
    text_content = models.TextField(
        blank=True,
        help_text='Will be truncated to 4500 characters or less '
                  '(at the nearest full sentence) by Amazon.')
    display_url = models.URLField(blank=True)

    class Meta:
        ordering = ('-published_date',)

    def __str__(self):
        return self.title

    def save(self, **kwargs):
        self.item_type = \
            Item.TYPE_AUDIO if self.audio_content else Item.TYPE_TEXT
        super(Item, self).save(**kwargs)
