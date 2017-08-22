import inspect
from importlib import import_module

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from sites_groups.widgets import SitesGroupsWidget
from jmbo.models import ModelBase

from listing.models import Listing, ListingContent, ListingPinned
from listing.styles import LISTING_CLASSES, LISTING_MAP


class ListingAdminForm(forms.ModelForm):

    # Content and pinned fields use "through" and require manual handling
    content_helper = forms.models.ModelMultipleChoiceField(
        label=_("Content"),
        queryset=ModelBase.objects.all().order_by("title"),
        required=False,
        help_text=_("Individual items to display. Setting this will ignore \
any setting for <i>Content Type</i>, <i>Categories</i> and <i>Tags</i>."),
    )
    pinned_helper = forms.models.ModelMultipleChoiceField(
        label=_("Pinned"),
        queryset=ModelBase.objects.all().order_by("title"),
        required=False,
        help_text=_("Individual items to pin to the top of the listing. These \
items are visible across all pages when navigating the listing."),
    )

    class Meta:
        model = Listing
        fields = (
            "title", "slug", "subtitle", "content_types", "categories", "tags",
            "content_helper", "pinned_helper",
            "style", "count", "items_per_page",
            "sites",
        )
        widgets = {
            "sites": SitesGroupsWidget,
            "style": forms.widgets.RadioSelect
        }

    def __init__(self, *args, **kwargs):

        # Initial through values must be set here else the widgets get the
        # initial order wrong.
        instance = kwargs.get("instance")
        if instance:
            if not "initial" in kwargs:
                kwargs["initial"] = {}
            kwargs["initial"]["content_helper"] = \
                [o.modelbase_obj for o in ListingContent.objects.filter(
                    listing=instance).order_by("position")]
            kwargs["initial"]["pinned_helper"] = \
                [o.modelbase_obj for o in ListingPinned.objects.filter(
                    listing=instance).order_by("position")]

        super(ListingAdminForm, self).__init__(*args, **kwargs)

        # Limit content_types vocabulary. Cannot do it with limit_choices_to.
        ids = []
        for obj in ContentType.objects.all():
            if (obj.model_class() is not None) and issubclass(obj.model_class(), ModelBase):
               ids.append(obj.id)
        self.fields["content_types"]._set_queryset(ContentType.objects.filter(id__in=ids).order_by("model"))

        # Style
        choices = []
        for kls in LISTING_CLASSES:
            image_path = getattr(kls, "image_path", None)
            image_markup = ""
            if image_path:
                image_markup = \
                    "<img src=\"%s%s\" style=\"max-width: 128px;\" />" \
                        % (settings.STATIC_URL.rstrip("/"), image_path)
            choices.append((
                kls.__name__,
                mark_safe("%s%s" % (image_markup, kls.__name__))
            ))
        self.fields["style"].widget.choices = choices

    def clean(self):
        super(ListingAdminForm, self).clean()
        for site in self.cleaned_data["sites"]:
            q = Listing.objects.filter(slug=self.cleaned_data["slug"], sites=site)
            if self.instance.id:
                q = q.exclude(id=self.instance.id)
            if q.exists():
                raise forms.ValidationError(_(
                    "The slug is already in use by listing %s. To use the same \
                    slug the listings may not have overlapping sites." % q[0]
                ))
        return self.cleaned_data

    def save(self, commit=True):
        instance = super(ListingAdminForm, self).save(commit=False)

        # Set through fields. Requires m2m trickery.
        old_save_m2m = self.save_m2m
        def save_m2m():
            old_save_m2m()
            ListingContent.objects.filter(listing=instance).delete()
            for n, obj in enumerate(self.cleaned_data["content_helper"]):
                ListingContent.objects.create(
                    modelbase_obj=obj, listing=instance, position=n
                )
            ListingPinned.objects.filter(listing=instance).delete()
            for n, obj in enumerate(self.cleaned_data["pinned_helper"]):
                ListingPinned.objects.create(
                    modelbase_obj=obj, listing=instance, position=n
                )
        self.save_m2m = save_m2m

        if commit:
            instance.save()
            self.save_m2m()

        return instance


class ListingAdmin(admin.ModelAdmin):
    form = ListingAdminForm
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "subtitle", "style", "_layout", "_get_absolute_url")

    def _get_absolute_url(self, obj):
        url = obj.get_absolute_url()
        return """<a href="%s" target="public">%s</a>""" % (url, url)
    _get_absolute_url.short_description = "Permalink"
    _get_absolute_url.allow_tags = True

    def _layout(self, obj):
        pth = getattr(LISTING_MAP[obj.style], "image_path", None)
        if pth:
            return """<img src="%s%s" style="max-width: 128px;" />""" % (settings.STATIC_URL, pth)
        return ""
    _layout.short_description = "Layout"
    _layout.allow_tags = True


admin.site.register(Listing, ListingAdmin)
