import uuid
from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from django.utils.translation import ugettext_lazy as _
from adminsortable.models import SortableMixin
from cms.models.fields import PlaceholderField
from djangocms_text_ckeditor.fields import HTMLField
from filer.fields.image import FilerImageField


class Group(TranslatableModel, SortableMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(_('Slug'), max_length=255)
    translations = TranslatedFields(
        title=models.CharField(_('Title'), max_length=255),
    )

    position = models.PositiveIntegerField(_('Position'), default=0, editable=False, db_index=True)
    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')
        ordering = ['position']

    def __str__(self):
        return self.title


class Person(TranslatableModel, SortableMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(_('Slug'), max_length=255)

    translations = TranslatedFields(
        full_name=models.CharField(_('Full name'), max_length=255),
        role=models.CharField(_('Role'), max_length=255, blank=True, default=''),
        description=HTMLField(_('Description'), blank=True, default='')
    )

    groups = models.ManyToManyField(Group, blank=True, related_name='people')
    bio = PlaceholderField('person_bio')
    photo = FilerImageField(
        verbose_name=_('Photo'),
        blank=True,
        help_text=_('Optional. Please supply a photo of this person.'),
        null=True,
        on_delete=models.SET_NULL,
    )

    position = models.PositiveIntegerField(_('Position'), default=0, editable=False, db_index=True)
    active = models.BooleanField(_('Active'), default=True)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Person')
        verbose_name_plural = _('People')
        ordering = ['position']

    def __str__(self):
        return self.full_name
