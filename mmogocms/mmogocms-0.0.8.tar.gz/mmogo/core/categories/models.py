from django.db import models
from django.core.urlresolvers import reverse
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.translation import ugettext_lazy as _


class Category(MPTTModel):
    title = models.CharField(
        max_length=255,
        help_text=_("The name of the product.")
    )
    slug = models.SlugField(
        help_text=_("The machine readable name of product")
    )
    subtitle = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("")
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text=_("")
    )
    parent = TreeForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        db_index=True
    )
    image = models.ImageField(
        upload_to='categories',
        blank=True
    )

    class MPTTMeta:
        order_insertion_by = ['title']


    def get_absolute_url(self):
        return reverse('category', kwargs={'path': self.get_path()})


    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        if self.subtitle:
            return self.title + ' - ' + self.subtitle
        else:
            return self.title
