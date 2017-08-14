from django.contrib import admin
from django.db import models
from mptt.admin import MPTTModelAdmin
from django.utils.translation import ugettext_lazy as _
from adminsortable.admin import NonSortableParentAdmin, SortableTabularInline
from django.utils.safestring import mark_safe
from cms.admin.placeholderadmin import FrontendEditableAdminMixin
from pcart_treeadmin.admin import TreeAdmin
from pagedown.widgets import AdminPagedownWidget
from .models import (
    Collection,
    ProductType,
    ProductTypeProperty,
    ProductStatus,
    Product,
    ProductVariant,
    ProductImage,
    Vendor,
    PropertyValueSlug,
)
from .forms import EditProductVariantForm, EditProductVariantFormSet


class VendorAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'id')
    search_fields = ['title', 'slug', 'id']
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Vendor, VendorAdmin)


class CollectionAdmin(TreeAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ('title_preview', 'changed', 'published', 'site', 'slug')
    list_filter = ('published', 'site')
    preserve_filters = True
    search_fields = ['title', 'id']
    fieldsets = (
        (None, {
            'fields': ('site', 'title', 'slug', 'parent', 'description', 'image'),
        }),
        (_('SEO'), {
            'fields': ('page_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Filters'), {
            'fields': (
                'custom_url_filter_rules',
                'url_filter_rules',
                'show_vendor_filter', 'show_properties_filters', 'exclude_properties_filters',
                'show_price_filter',
            ),
        }),
        (_('Publication'), {
            'fields': ('published',),
        }),
    )

    def title_preview(self, obj):
        return mark_safe('%s%s' % ('&nbsp;'*obj.level*4, obj.title))
    title_preview.short_description = _('Title')
    title_preview.admin_order_field = 'title'

admin.site.register(Collection, CollectionAdmin)


class ProductTypePropertyInline(SortableTabularInline):
    model = ProductTypeProperty
    extra = 1


class ProductTypeAdmin(NonSortableParentAdmin):
    list_display = ('title', 'id')
    search_fields = ['title']
    inlines = [ProductTypePropertyInline]

admin.site.register(ProductType, ProductTypeAdmin)


class ProductStatusAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'show_buy_button', 'is_visible', 'is_searchable', 'weight')
    search_fields = ['title']

admin.site.register(ProductStatus, ProductStatusAdmin)


class ProductImageInline(SortableTabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    readonly_fields = ['tags']
    form = EditProductVariantForm
    formset = EditProductVariantFormSet
    extra = 1

    def get_fields(self, request, obj=None):
        exclude_prop_fields = tuple(p[0] for p in obj.get_properties_fields(for_variants=True))
        self.exclude = exclude_prop_fields
        fields = ('title', 'slug', 'tags', 'sku', 'barcode', 'status', 'price', 'compare_at_price', 'price_varies') + exclude_prop_fields
        return fields


class ProductAdmin(FrontendEditableAdminMixin, NonSortableParentAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = (
        'show_title',
        'vendor',
        'status',
        'show_price',
        'product_type',
        'get_collections',
        'published', 'slug')
    list_filter = ('published', 'collections', 'product_type')
    filter_horizontal = ('collections',)
    preserve_filters = True
    search_fields = ['title', 'id']
    inlines = [ProductImageInline, ProductVariantInline]
    save_as_continue = True

    def get_queryset(self, request):
        queryset = super(ProductAdmin, self).get_queryset(request)
        queryset = queryset\
            .prefetch_related('vendor')\
            .prefetch_related('status') \
            .prefetch_related('product_type') \
            .prefetch_related('collections')
        return queryset

    def show_price(self, obj):
        if obj.variants_count > 0:
            return '%s - %s' % (obj.min_variant_price, obj.max_variant_price)
        else:
            if obj.compare_at_price != 0:
                return '%s --%s--' % (obj.price, obj.compare_at_price)
            else:
                return '%s' % obj.price
    show_price.short_description = _('Price')
    show_price.admin_order_field = 'min_variant_price'

    def get_collections(self, obj):
        return ', '.join([x.title for x in obj.collections.all()])
    get_collections.short_description = _('Collections')

    def show_title(self, obj):
        from django.utils.html import format_html
        if obj.variants_count > 0:
            return format_html(
                '{0} <span style="float:right;"><strong>({1})</strong></span>',
                obj.title,
                obj.variants_count)
        else:
            return obj.title
    show_title.short_description = _('Title')
    show_title.admin_order_field = 'title'

    def get_form(self, request, obj=None, **kwargs):
        from .forms import AddProductForm, EditProductForm
        if obj is None:
            kwargs['form'] = AddProductForm
        else:
            kwargs['form'] = EditProductForm
        return super(ProductAdmin, self).get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            self.exclude = []
            return (
                (None, {
                    'fields': ('title', 'slug', 'product_type', 'vendor', 'status'),
                }),
            )
        else:
            exclude_prop_fields = tuple(p[0] for p in obj.get_properties_fields())
            self.exclude = exclude_prop_fields
            return (
                (None, {
                    'fields': (
                        'title', 'slug', 'external_id', 'product_type', 'vendor', 'description'),
                }),
                (_('SEO'), {
                    'fields': ('page_title', 'meta_description'),
                    'classes': ('collapse',),
                }),
                (_('Tags'), {
                    'fields': ('tags', 'sku', 'barcode', 'status', 'quantity'),
                }),
                (_('Properties'), {
                    'fields': exclude_prop_fields,
                }),
                (_('Price'), {
                    'fields': ('price', 'compare_at_price', 'price_varies', 'max_variant_price', 'min_variant_price'),
                }),
                (_('Shipping'), {
                    'fields': ('weight',),
                    'classes': ('collapse',),
                }),
                (_('Publication'), {
                    'fields': ('collections', 'published', 'variants_count', 'added', 'changed'),
                }),
            )

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide ProductVariantInline in the add view
            if isinstance(inline, ProductVariantInline) and obj is None:
                continue
            yield inline.get_formset(request, obj), inline

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return []
        else:
            if obj.variants_count == 0:
                return (
                    'product_type',
                    'tags',
                    'min_variant_price',
                    'max_variant_price',
                    'variants_count',
                    'added',
                    'changed',
                )
            else:
                return (
                    'product_type',
                    'tags',
                    'status',
                    'min_variant_price',
                    'max_variant_price',
                    'variants_count',
                    'added',
                    'changed',
                )

admin.site.register(Product, ProductAdmin)


class PropertyValueSlugAdmin(admin.ModelAdmin):
    list_display = ('value', 'slug')
    search_fields = ('value', 'slug')

admin.site.register(PropertyValueSlug, PropertyValueSlugAdmin)
