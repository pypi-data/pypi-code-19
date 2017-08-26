from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _

NAMESPACE_CHOICES = (
    (namespace_, namespace.get('title', namespace_)) for \
            namespace_, namespace in \
            settings.THORSONWIKI_NAMESPACES.items()
)

@python_2_unicode_compatible
class Article(models.Model):
    """
    A wiki article. Users can create, edit, and delete articles. 
    """

    #: The article's title.
    title = models.CharField(_("title"), blank=False, max_length=255,
            help_text=_("The title of this article."))

    #: The article's title, slugified for URLs.
    slug = models.SlugField(_("slug"), blank=True, max_length=255,
            editable=False, help_text=_("The article's title, " \
                    " slugified for URLs."))

    #: The article's namespace.
    namespace = models.CharField(_("namespace"), blank=False, max_length=255,
            choices=NAMESPACE_CHOICES, 
            help_text=_("The article's namespace."))

    #: The content of the article.
    content = models.TextField(_("content"), blank=True,
            help_text=_("The content of the article."))

    #: Whether the article is completely public.
    public = models.BooleanField(_("public"), default=True,
            help_text=_("Whether the article is completely public."))

    #: Allows this article to redirect to another one.
    redirect = models.CharField(_("redirect to"), blank=True, max_length=255,
            help_text=_("Allows this article to redirect to another one."))

    def __str__(self):

        return self.title

    def can_edit(self, user):
        """
        Returns True if the given user has permission to edit this article.
        """

        return user.has_perm('thorson_wiki.edit-article:%s' % self.slug)

    def can_read(self, user):
        """
        Returns True if the given user has permission to read this article.
        """

        if self.public:
            return True

        return user.has_perm('thorson_wiki.read-article:%s' % self.slug)

    def clean(self):

        # Require that slugs and titles be unique within a namespace
        query = ~models.Q(pk=self.pk) & \
                models.Q(namespace=self.namespace)

        queryset = Article.objects.filter(query)

        if queryset.filter(title__iexact=self.title).exists():
            raise ValidationError(_("Article titles must be unique" \
                    " within a namespace."))

        if queryset.filter(slug__iexact=self.slug).exists():
            raise ValidationError(_("Slugs must be unique within" \
                    " a namespace."))

        return super(Article, self).clean()

    def get_absolute_url(self):

        return reverse_lazy(self.namespace + ':article',
                args=[self.slug])

    class Meta:

        verbose_name = _("article")
        verbose_name_plural = _("articles")
