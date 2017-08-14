from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.urls import reverse, NoReverseMatch
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
# from django.utils.functional import lazy
from django.core.cache import cache
from adminsortable.fields import SortableForeignKey
from adminsortable.models import SortableMixin
from mptt.models import MPTTModel, TreeForeignKey
from cms.models import CMSPlugin
import uuid


class ProductType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('Title'), max_length=255, unique=True)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Product type')
        verbose_name_plural = _('Product types')
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_properties_fields(self, initial_values={}, for_variants=False):
        from django import forms
        if for_variants:
            properties = self.properties.filter(for_variants=True)
        else:
            properties = self.properties.all()
        result = [
            (
                'property_%s' % i,
                p.title,
                forms.CharField(label=p.title, initial=initial_values.get(p.title) or p.default_value, required=False),
            ) for i, p in enumerate(properties)]
        return result


class ProductTypeProperty(SortableMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('Title'), max_length=255)

    default_value = models.CharField(_('Default value'), max_length=255, blank=True)
    tag_prefix = models.CharField(_('Tag prefix'), max_length=10, blank=True)

    use_in_filters = models.BooleanField(_('Use in filters'), default=False)
    for_variants = models.BooleanField(_('For variants'), default=False)

    product_type = SortableForeignKey(ProductType, verbose_name=_('Product type'), related_name='properties')

    position = models.PositiveIntegerField(_('Position'), default=0, editable=False, db_index=True)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Product type property')
        verbose_name_plural = _('Product type properties')
        ordering = ['position']

    def __str__(self):
        return self.title


# Listen for signals for ProductTypeProperty

@receiver(pre_save, sender=ProductTypeProperty)
def product_type_pre_save_listener(sender, instance, **kwargs):
    _resaved = False
    if instance.pk:
        from .tasks import rename_property_name, update_product_tags
        product_type_id = instance.product_type_id
        try:
            ptp = ProductTypeProperty.objects.get(pk=instance.pk)
            old_title = ptp.title
            new_title = instance.title
            if old_title != new_title:
                rename_property_name.delay(product_type_id, old_title, new_title)
                _resaved = True
            if not _resaved and ptp.tag_prefix != instance.tag_prefix:
                update_product_tags.delay(product_type_id, new_title)
        except ProductTypeProperty.DoesNotExist:
            pass


def generate_collection_image_filename(instance, filename):
    ext = filename.split('.')[-1]
    url = 'images/collections/%s/%s.%s' % (instance.id, str(uuid.uuid4()).replace('-', ''), ext)
    return url


class Collection(MPTTModel):

    DEFAULT_URL_FILTER_RULES = '''VENDOR
PRICE'''

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(
        Site, verbose_name=_('Site'), related_name='collections', on_delete=models.PROTECT)
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'))
    parent = TreeForeignKey(
        'self', null=True, blank=True, related_name='children', db_index=True,
        verbose_name=_('Parent'),
    )

    image = models.ImageField(_('Image'), null=True, blank=True, upload_to=generate_collection_image_filename)
    description = models.TextField(_('Description'), blank=True)

    page_title = models.CharField(_('Page title'), max_length=255, blank=True)
    meta_description = models.TextField(_('Meta description'), blank=True)

    custom_url_filter_rules = models.BooleanField(_('Custom URL filter rules'), default=False)
    url_filter_rules = models.TextField(
        _('URL filter rules'), blank=True, default=DEFAULT_URL_FILTER_RULES,
        help_text=_('Use separate lines for different rules. See documentation for details.')
    )

    show_vendor_filter = models.BooleanField(_('Show vendor filter'), default=True)
    show_properties_filters = models.BooleanField(_('Show properties filters'), default=True)
    exclude_properties_filters = ArrayField(
        models.CharField(max_length=70),
        verbose_name=_('Exclude properties filters'), default=list, blank=True,
        help_text=_('Comma separated list of properties labels which you want to exclude from filters.'),
    )
    show_price_filter = models.BooleanField(_('Show price filter'), default=True)

    published = models.BooleanField(_('Published'), default=True)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Collection')
        verbose_name_plural = _('Collections')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        try:
            return reverse('pcart_collection:product-list-for-collection', args=[self.slug])
        except NoReverseMatch:
            return '#no-page-for-collection-app'

    def as_dict(self):
        result = {
            'id': self.id,
            'title': self.title,
            'site': {'domain': self.site.domain, 'name': self.site.name},
            'slug': self.slug,
            'parent': self.parent_id,
            'description': self.description,
            'page_title': self.page_title,
            'published': self.published,
            'added': self.added,
            'changed': self.changed,
            'url': self.get_absolute_url(),
        }
        return result

    def get_url_filter_rules(self):
        if self.custom_url_filter_rules:
            return self.url_filter_rules
        else:
            _cache_key = 'url-filter-rules-%s' % self.pk
            result = cache.get(_cache_key)
            if result:
                return result

            _product_types = ProductType.objects.filter(products__collections=self).distinct()
            _filter_rules = []
            if self.show_vendor_filter:
                _filter_rules.append('VENDOR')
            if self.show_properties_filters:
                for p_type in _product_types:
                    f_props = p_type.properties.filter(use_in_filters=True)
                    for prop in f_props:
                        if prop.title not in self.exclude_properties_filters:
                            _filter_rules.append('TAG/+%s/VALUE ONLY IGNORE DASH' % prop.tag_prefix)
            if self.show_price_filter:
                _filter_rules.append('PRICE')
            result = '\n'.join(_filter_rules)
            cache.set(_cache_key, result, 60*15)    # save for 15 min
            return result

class ProductStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('Title'), max_length=255, unique=True)

    show_buy_button = models.BooleanField(_('Show buy button'), default=True)
    is_visible = models.BooleanField(_('Is visible'), default=True)
    is_searchable = models.BooleanField(_('Is searchable'), default=True)

    weight = models.PositiveIntegerField(_('Weight'), default=0)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Product status')
        verbose_name_plural = _('Product statuses')
        ordering = ['id']  # TODO: change to weight

    def __str__(self):
        return self.title

    def as_dict(self):
        result = {
            'id': self.id,
            'title': self.title,
            'show_buy_button': self.show_buy_button,
            'is_visible': self.is_visible,
            'is_searchable': self.is_searchable,
            'weight': self.weight,
        }
        return result


def generate_vendor_image_filename(instance, filename):
    ext = filename.split('.')[-1]
    url = 'images/vendors/%s/%s.%s' % (instance.id, str(uuid.uuid4()).replace('-', ''), ext)
    return url


class Vendor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('Title'), max_length=255, unique=True)
    slug = models.SlugField(_('Slug'), max_length=255)
    image = models.ImageField(_('Image'), null=True, blank=True, upload_to=generate_vendor_image_filename)

    class Meta:
        verbose_name = _('Vendor')
        verbose_name_plural = _('Vendors')
        ordering = ['title']

    def __str__(self):
        return self.title

    def as_dict(self):
        result = {
            'id': self.id,
            'title': self.title,
        }
        return result


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255)
    description = models.TextField(_('Description'), blank=True)
    external_id = models.CharField(
        _('External ID'), default='', blank=True, max_length=255, db_index=True)

    page_title = models.CharField(_('Page title'), max_length=255, blank=True)
    meta_description = models.TextField(_('Meta description'), blank=True)

    vendor = models.ForeignKey(
        Vendor, verbose_name=_('Vendor'), related_name='products', null=True, blank=True, on_delete=models.SET_NULL)
    product_type = models.ForeignKey(
        ProductType, verbose_name=_('Product type'), related_name='products', on_delete=models.CASCADE)
    collections = models.ManyToManyField(
        Collection, verbose_name=_('Collections'), related_name='products', blank=True,
        help_text=_('Add this product to a collection so it\'s easy to find in your store.'),
    )

    tags = ArrayField(
        models.CharField(max_length=30),
        verbose_name=_('Tags'),
        blank=True,
        default=list,
    )
    properties = JSONField(_('Properties'), default=dict, blank=True)

    sku = models.CharField(_('SKU (Stock Keeping Unit)'), blank=True, max_length=100)
    barcode = models.CharField(_('Barcode (ISBN, UPC, GTIN, etc.)'), blank=True, max_length=100)

    status = models.ForeignKey(
        ProductStatus, verbose_name=_('Status'), related_name='products', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(_('Quantity'), default=None, null=True, blank=True)

    price = models.DecimalField(_('Price'), max_digits=10, decimal_places=2, default=0.00)
    compare_at_price = models.DecimalField(_('Compare at price'), max_digits=10, decimal_places=2, default=0.00)
    price_varies = models.BooleanField(_('Price varies'), default=False)

    # Set automatically with stored procedure. For read only access.
    max_variant_price = models.DecimalField(_('Max variant price'), max_digits=10, decimal_places=2, default=0.00)
    min_variant_price = models.DecimalField(_('Min variant price'), max_digits=10, decimal_places=2, default=0.00)
    variants_count = models.PositiveIntegerField(_('Variants count'), default=0)

    weight = models.FloatField(
        _('Weight (kg)'), default=0.0, help_text=_('Used to calculate shipping rates at checkout.'))

    published = models.BooleanField(_('Published'), default=True)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['id']

    def __str__(self):
        return self.title

    @staticmethod
    def type():
        return 'product'

    def get_absolute_url(self):
        try:
            return reverse('pcart_product:product-detail', args=[self.slug])
        except NoReverseMatch:
            return '#no-page-for-product-app'

    def get_properties_fields(self, initial_values=None, for_variants=False):
        return self.product_type.get_properties_fields(
            initial_values=self.properties if initial_values is None else initial_values,
            for_variants=for_variants)

    def has_variants(self):
        return self.variants_count > 0

    def get_image(self):
        return self.images.first()

    def available(self):
        return self.variants_count == 0 and self.price > 0 and self.status.show_buy_button

    def as_dict(self):
        result = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'page_title': self.page_title,
            'tags': self.tags,
            'properties': self.properties,
            'sku': self.sku,
            'barcode': self.barcode,
            'status': self.status.as_dict(),
            'price': self.price,
            'price_varies': self.price_varies,
            'compare_at_price': self.compare_at_price,
            'max_variant_price': self.max_variant_price,
            'min_variant_price': self.min_variant_price,
            'variants_count': self.variants_count,
            'weight': self.weight,
            'published': self.published,
            'url': self.get_absolute_url(),
        }
        return result

    def get_page_title(self, request=None):
        return self.page_title or self.title


@receiver(post_save, sender=Product)
def product_post_save_listener(sender, instance, **kwargs):
    from .utils import filter_non_numeric_tags
    tagset = instance.tags
    values = filter_non_numeric_tags(tagset)
    PropertyValueSlug.objects.add_values(values)


class ProductVariant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'), unique=False, max_length=255)
    external_id = models.CharField(
        _('External ID'), default='', blank=True, max_length=255, db_index=True)

    product = models.ForeignKey(
        Product, verbose_name=_('Product'), related_name='variants', on_delete=models.CASCADE)

    tags = ArrayField(
        models.CharField(max_length=30),
        verbose_name=_('Tags'),
        blank=True,
        default=list,
    )
    properties = JSONField(_('Properties'), default=dict, blank=True)

    sku = models.CharField(_('SKU (Stock Keeping Unit)'), blank=True, max_length=100)
    barcode = models.CharField(_('Barcode (ISBN, UPC, GTIN, etc.)'), blank=True, max_length=100)

    status = models.ForeignKey(ProductStatus, verbose_name=_('Status'), related_name='variants')
    quantity = models.PositiveIntegerField(_('Quantity'), default=None, null=True, blank=True)

    price = models.DecimalField(_('Price'), max_digits=10, decimal_places=2, default=0.00)
    compare_at_price = models.DecimalField(_('Compare at price'), max_digits=10, decimal_places=2, default=0.00)
    price_varies = models.BooleanField(_('Price varies'), default=False)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    class Meta:
        verbose_name = _('Product variant')
        verbose_name_plural = _('Product variants')
        ordering = ['id']
        unique_together = ['product', 'slug']

    def __str__(self):
        return self.title

    @staticmethod
    def type():
        return 'variant'

    def get_absolute_url(self):
        try:
            return reverse('pcart_product:product-variant-detail', args=[self.product.slug, self.slug])
        except NoReverseMatch:
            return '#no-page-for-product-app'

    def get_properties_fields(self, initial_values=None):
        return self.product.product_type.get_properties_fields(
            initial_values=self.properties if initial_values is None else initial_values,
            for_variants=True)

    def get_image(self):
        return self.product.get_image()

    def weight(self):
        return self.product.weight

    def available(self):
        return self.price > 0 and self.status.show_buy_button


def generate_product_image_filename(instance, filename):
    ext = filename.split('.')[-1]
    url = 'images/products/%s/%s.%s' % (instance.product.id, str(uuid.uuid4()).replace('-', ''), ext)
    return url


class ProductImage(SortableMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('Title'), max_length=255, default='', blank=True)
    product = SortableForeignKey(
        Product, verbose_name=_('Product'), related_name='images', on_delete=models.CASCADE)

    image = models.ImageField(_('Image'), null=True, blank=True, upload_to=generate_product_image_filename)
    html_snippet = models.TextField(_('HTML snippet'), default='', blank=True)

    tags = ArrayField(
        models.CharField(max_length=30),
        verbose_name=_('Tags'),
        blank=True,
        default=list,
    )

    download_link = models.CharField(_('Download link'), max_length=300, default='', blank=True)
    downloaded = models.BooleanField(_('Downloaded'), default=False)

    added = models.DateTimeField(_('Added'), auto_now_add=True)
    changed = models.DateTimeField(_('Changed'), auto_now=True)

    position = models.PositiveIntegerField(_('Position'), default=0, editable=False, db_index=True)

    class Meta:
        verbose_name = _('Product image')
        verbose_name_plural = _('Product images')
        ordering = ['position']

    def __str__(self):
        return self.title or self.product.title

    def download_product_image(self, save=False):
        from django.core.files import File
        from ftplib import FTP
        from io import BytesIO
        import urllib.request
        import urllib.parse
        import os
        _changed = False
        o = urllib.parse.urlparse(self.download_link)

        if self.downloaded is False:
            if o.scheme in ['http', 'https']:
                # Download an image via HTTP
                local_filename, headers = urllib.request.urlretrieve(self.download_link)
                self.image.save(
                    os.path.basename(o.path),
                    File(open(local_filename, 'rb')),
                    save=False,
                )
                self.downloaded = True
                _changed = True
            elif o.scheme == 'ftp':
                # Download an image via FTP
                _ftp_sources = getattr(settings, 'PCART_FTP_IMAGE_SOURCES', {})
                _credentials = _ftp_sources.get(o.netloc)
                with FTP(o.netloc) as ftp:
                    if _credentials:
                        ftp.login(_credentials.get('user'), _credentials.get('password'))
                    else:
                        ftp.login()
                    ftp.getwelcome()
                    r = BytesIO()
                    ftp.retrbinary('RETR ~/%s' % o.path, r.write)
                    r.seek(0)

                    self.image.save(
                        os.path.basename(o.path),
                        File(r),
                        save=False,
                    )
                    self.downloaded = True
                    _changed = True

        if save and _changed:
            self.save()

    def save(self, *args, **kwargs):
        if self.downloaded is False and self.download_link:
            self.download_product_image(save=False)
        super(ProductImage, self).save(*args, **kwargs)


@receiver(pre_save, sender=ProductImage)
def product_image_pre_save_listener(sender, instance, **kwargs):
    if instance.pk:
        try:
            p_im = ProductImage.objects.get(pk=instance.pk)
            if p_im.image and p_im.image != instance.image:
                p_im.image.delete(save=False)
        except ProductImage.DoesNotExist:
            pass


@receiver(post_delete, sender=ProductImage)
def product_image_post_delete_listener(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)


class PropertyValueSlugManager(models.Manager):
    def generate_unique_slug(self, value):
        from pcart_core.utils import get_unique_slug
        slug = get_unique_slug(value, self.model)
        return slug

    def add_values(self, values=[]):
        values = list(set(values))
        existing_values = self.filter(value__in=values).values_list('value', flat=True)
        for v in values:
            if v not in existing_values:
                slug = self.generate_unique_slug(v)
                item = self.model(value=v, slug=slug)
                item.save(using=self._db)

    def update_data(self, products=None):
        from .utils import get_unique_tagset, filter_non_numeric_tags
        values = filter_non_numeric_tags(get_unique_tagset(products))
        self.add_values(values)


class PropertyValueSlug(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    value = models.CharField(_('Value'), max_length=255, unique=True)
    slug = models.SlugField(_('Slug'), max_length=255)

    objects = PropertyValueSlugManager()

    class Meta:
        verbose_name = _('Property value slug')
        verbose_name_plural = _('Property values slugs')
        ordering = ['value']

    def __str__(self):
        return self.value


# DjangoCMS plugins


class CollectionPluginModel(CMSPlugin):
    """ Represents a plugin with a products from the specified collection.
    """
    collection = TreeForeignKey(Collection, verbose_name=_('Collection'))
    filter_string = models.CharField(
        _('Filter string'), default='', blank=True, max_length=255,
        help_text=_('Use the list of filter chunks separated with / and ; characters.')
    )
    sorting = models.CharField(_('Sorting'), default='', blank=True, max_length=100)
    template_name = models.CharField(_('Template name'), default='', blank=True, max_length=100)

    def __init__(self, *args, **kwargs):
        super(CollectionPluginModel, self).__init__(*args, **kwargs)
        # self._meta.get_field_by_name('sorting')[0]._choices = get_plugin_sorting_choices()
        # self._meta.get_field_by_name('template_name')[0]._choices = get_plugin_template_choices()

    def __str__(self):
        return str(self.collection)
