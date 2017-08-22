from django.db import models, connection
from django.db.models import Q
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from jmbo.models import ModelBase

from listing.styles import LISTING_CLASSES
from listing.managers import PermittedManager


class AttributeWrapper:
    """Wrapper that allows attributes to be added or overridden on an object"""

    def __init__(self, obj, **kwargs):
        self._obj = obj
        self._attributes = {}
        for k, v in kwargs.items():
            self._attributes[k] = v

    def __getattr__(self, key):
        if key in self._attributes:
            return self._attributes[key]
        return getattr(self._obj, key)

    def __setstate__(self, dict):
        self.__dict__.update(dict)

    @property
    def klass(self):
        """Can"t override __class__ and making it a property also does not
        work. Could be because of Django metaclasses."""
        return self._obj.__class__


class Listing(models.Model):

    title = models.CharField(
        max_length=256,
        help_text="A short descriptive title.",
    )
    subtitle = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        help_text="Some titles may be the same. A subtitle makes a distinction. It is not displayed on the site.",
    )
    slug = models.SlugField(
        editable=True,
        max_length=32,
        db_index=True,
    )
    content_types = models.ManyToManyField(
        ContentType,
        help_text="Content types to display, eg. post or gallery.",
        blank=True,
    )
    content = models.ManyToManyField(
        "jmbo.ModelBase",
        help_text="""Individual items to display. Setting this will ignore \
any setting for <i>Content Type</i>, <i>Categories</i> and <i>Tags</i>.""",
        blank=True,
        related_name="listing_content",
        through="ListingContent",
    )
    categories = models.ManyToManyField(
        "category.Category",
        help_text="Categories for which to collect items.",
        blank=True,
        related_name="listing_categories"
    )
    tags = models.ManyToManyField(
        "category.Tag",
        help_text="Tags for which to collect items.",
        blank=True,
        related_name="listing_tags"
    )
    pinned = models.ManyToManyField(
        "jmbo.ModelBase",
        help_text="""Individual items to pin to the top of the listing. These
items are visible across all pages when navigating the listing.""",
        blank=True,
        related_name="listing_pinned",
        through="ListingPinned",
    )
    count = models.IntegerField(
        default=0,
        help_text="""Number of items to display (excludes any pinned items).
Set to zero to display all items.""",
    )
    style = models.CharField(
        choices=[(klass.__name__, klass.__name__) for klass in LISTING_CLASSES],
        max_length=64
    )
    items_per_page = models.PositiveIntegerField(
        default=0,
        help_text="Number of items displayed on a page (excludes any pinned items). Set to zero to disable paging."
    )
    sites = models.ManyToManyField(
        "sites.Site",
        blank=True,
        help_text="Sites that this listing will appear on.",
    )

    objects = models.Manager()
    permitted = PermittedManager()

    class Meta:
        ordering = ("title", "subtitle")

    def __unicode__(self):
        if self.subtitle:
            return "%s (%s)" % (self.title, self.subtitle)
        else:
            return self.title

    def get_absolute_url(self):
        #return reverse("listing-detail", args=[self.slug])
        # todo: fix
        return ""

    def _get_queryset(self, manager="objects"):
        # Due to the workaround we're not always returning a real queryset.
        content = self._get_content_queryset(manager=manager)
        if content:
            return content

        q = getattr(ModelBase, manager).all()
        one_match = False
        if self.content_types.exists():
            q = q.filter(content_type__in=self.content_types.all())
            one_match = True
        if self.categories.exists():
            q1 = Q(primary_category__in=self.categories.all())
            q2 = Q(categories__in=self.categories.all())
            q = q.filter(q1|q2)
            one_match = True
        if self.tags.exists():
            q = q.filter(tags__in=self.tags.all())
            one_match = True
        if not one_match:
            q = ModelBase.objects.none()
        # todo: use manager below
        q = q.exclude(id__in=self.pinned.all())

        # Ensure there are no duplicates. Oracle bugs and SQLite definciencies
        # require special handling around distinct which incur a performance
        # penalty when fetching attributes. Avoid the penalty for other
        # databases by doing database detection.
        if connection.vendor.lower() in ("oracle", "sqlite"):
            q = q.only("id").distinct()
        else:
            q = q.distinct("publish_on", "created", "id").order_by(
                "-publish_on", "-created"
            )

        if self.count:
            q = q[:self.count]

        return q

    @property
    def queryset(self):
        return self._get_queryset()

    @property
    def queryset_permitted(self):
        return self._get_queryset(manager="permitted")

    def set_pinned(self, iterable):
        for n, obj in enumerate(iterable):
            ListingPinned.objects.create(
                modelbase_obj=obj, listing=self, position=n
            )

    def set_content(self, iterable):
        for n, obj in enumerate(iterable):
            ListingContent.objects.create(
                modelbase_obj=obj, listing=self, position=n
            )

    def _get_content_queryset(self, manager="objects"):
        # I can't find a way to do this in a single query. Note we return an
        # emulated queryset.
        li = [o for o in getattr(ModelBase, manager).filter(listing_content=self)\
            .exclude(id__in=self.pinned.all())]
        order = [o.modelbase_obj.id for o in ListingContent.objects.filter(
            listing=self).order_by("position")]
        li.sort(lambda a, b: cmp(order.index(a.id), order.index(b.id)))
        return AttributeWrapper(li, exists=len(li))

    @property
    def content_queryset(self):
        return self._get_content_queryset()

    @property
    def content_queryset_permitted(self):
        return self._get_content_queryset(manager="permitted")

    def _get_pinned_queryset(self, manager="objects"):
        # I can't find a way to do this in a single query. Note we return an
        # emulated queryset.
        li = [o for o in getattr(ModelBase, manager).filter(listing_pinned=self)]
        order = [o.modelbase_obj.id for o in ListingPinned.objects.filter(
            listing=self).order_by("position")]
        li.sort(lambda a, b: cmp(order.index(a.id), order.index(b.id)))
        return AttributeWrapper(li, exists=len(li))

    @property
    def pinned_queryset(self):
        return self._get_pinned_queryset()

    @property
    def pinned_queryset_permitted(self):
        return self._get_pinned_queryset(manager="permitted")

    def __iter__(self):
        for obj in self.queryset_permitted:
            yield obj

    def __len__(self):
        # We can't use count because it's not a real queryset
        return len(self.queryset_permitted)


class ListingContent(models.Model):
    """Through model to facilitate ordering"""

    modelbase_obj = models.ForeignKey('jmbo.ModelBase')
    listing = models.ForeignKey(Listing, related_name="content_link_to_listing")
    position = models.PositiveIntegerField(default=0)


class ListingPinned(models.Model):
    """Through model to facilitate ordering"""

    modelbase_obj = models.ForeignKey('jmbo.ModelBase')
    listing = models.ForeignKey(Listing, related_name="pinned_link_to_listing")
    position = models.PositiveIntegerField(default=0)


@receiver(m2m_changed)
def check_slug(sender, **kwargs):
    """Slug must be unique per site"""
    instance = kwargs["instance"]
    if (kwargs["action"] == "post_add") \
        and sender.__name__.endswith("_sites") \
        and isinstance(instance, (Listing,)):
        for site in instance.sites.all():
            q = instance.__class__.objects.filter(slug=instance.slug, sites=site).exclude(id=instance.id)
            if q.exists():
                raise RuntimeError("The slug %s is already in use for site %s by %s" % (instance.slug, site.domain, q[0].title))

