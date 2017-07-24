import uuid
from django.utils import timezone
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse, NoReverseMatch
from parler.models import TranslatableModel, TranslatedFields
from cms.models.fields import PlaceholderField
from cms.models import CMSPlugin
from adminsortable.models import SortableMixin
from djangocms_text_ckeditor.fields import HTMLField
from filer.fields.image import FilerImageField


class Category(TranslatableModel, SortableMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(_('Slug'), max_length=255)
    translations = TranslatedFields(
        title=models.CharField(_('Title'), max_length=255),
    )

    position = models.PositiveIntegerField(_('Position'), default=0, editable=False, db_index=True)
    active = models.BooleanField(_('Active'), default=False)
    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['position']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        try:
            return '%s?category=%s' % (reverse('pcart_newsblog:articles'), self.slug)
        except NoReverseMatch:
            return '#no-page-for-newsblog-app'


class Article(TranslatableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(_('Slug'), max_length=255)
    category = models.ForeignKey(
        Category, verbose_name=_('Category'), related_name='articles', null=True, blank=True,
        on_delete=models.CASCADE,
    )

    translations = TranslatedFields(
        title=models.CharField(_('Title'), max_length=255, unique=True),
        lead_in=HTMLField(
            verbose_name=_('Lead'), default='',
            help_text=_(
                'The lead gives the reader the main idea of the story, this '
                'is useful in overviews, lists or as an introduction to your '
                'article.'
            ),
            blank=True,
        ),
        page_title=models.CharField(
            max_length=255, verbose_name=_('Page title'),
            blank=True, default=''),
        meta_description=models.TextField(
            verbose_name=_('Meta description'), blank=True, default=''),
        meta_keywords=models.TextField(
            verbose_name=_('Meta keywords'), blank=True, default=''),
    )

    author = models.ForeignKey(
        'pcart_people.Person', verbose_name=_('Author'), null=True, blank=True, related_name='articles',
        on_delete=models.CASCADE,
    )
    content = PlaceholderField('newsblog_article_content', related_name='newsblog_article_content')
    lead_image = FilerImageField(
        verbose_name=_('Photo'),
        blank=True,
        help_text=_('Optional. Please supply a photo of this person.'),
        null=True,
        on_delete=models.SET_NULL,
    )
    tags = ArrayField(
        models.CharField(max_length=30),
        verbose_name=_('Tags'),
        blank=True,
        default=list,
    )

    published = models.BooleanField(_('Published'), default=False)
    pub_date = models.DateTimeField(_('Publication date'), default=timezone.now)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
        ordering = ['-pub_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        try:
            return reverse('pcart_newsblog:article', args=[self.slug])
        except NoReverseMatch:
            return '#no-page-for-newsblog-app'


# DjangoCMS plugins


class ArticleBlockPluginModel(CMSPlugin):
    """ Represents a plugin with a lead text of an article.
    """
    article = models.ForeignKey(Article, verbose_name=_('Article'))
    template_name = models.CharField(_('Template name'), default='', blank=True, max_length=100)

    def __init__(self, *args, **kwargs):
        super(ArticleBlockPluginModel, self).__init__(*args, **kwargs)

    def __str__(self):
        return str(self.article)
