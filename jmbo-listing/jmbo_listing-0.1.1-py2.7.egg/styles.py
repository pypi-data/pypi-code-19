import inspect
from importlib import import_module

from django.template.loader import render_to_string
from django.conf import settings


class AbstractBaseStyle(object):
    image_path = "/admin/listing/images/unknown.png"

    def __init__(self, listing):
        self.listing = listing

    def get_queryset(self):
        return self.listing.queryset_permitted

    def get_pinned_queryset(self):
        # Check for pinned_queryset. It can be missing since listings can be
        # called via the {% listing %} tag. The resulting proxy listing object
        # does not neccessarily have the property.
        from jmbo.models import ModelBase
        return getattr(self.listing, "pinned_queryset_permitted", ModelBase.objects.none())

    def get_context_data(self, context, as_tile=False):
        context["object_list"] = self.get_queryset()
        context["pinned_list"] = self.get_pinned_queryset()
        context["listing"] = self.listing
        context["items_per_page"] = self.listing.items_per_page
        context["identifier"] = getattr(self.listing, "id", None) \
            or getattr(self.listing, "identifier", "")
        return context

    def render(self, context, as_tile=False):
        context.push()
        new_context = self.get_context_data(context, as_tile=as_tile)
        result = render_to_string(self.template_name, new_context.flatten())
        context.pop()
        return result


class Horizontal(AbstractBaseStyle):
    template_name = "listing/templatetags/horizontal.html"
    image_path = "/admin/listing/images/horizontal.png"


class Vertical(AbstractBaseStyle):
    template_name = "listing/templatetags/vertical.html"
    image_path = "/admin/listing/images/vertical.png"


class Promo(AbstractBaseStyle):
    template_name = "listing/templatetags/promo.html"
    image_path = "/admin/listing/images/promo.png"


class VerticalThumbnail(AbstractBaseStyle):
    template_name = "listing/templatetags/vertical_thumbnail.html"
    image_path = "/admin/listing/images/vertical-thumbnail.png"


class Widget(AbstractBaseStyle):
    template_name = "listing/templatetags/widget.html"
    image_path = "/admin/listing/images/widget.png"


class CustomOne(AbstractBaseStyle):
    template_name = "listing/templatetags/custom_one.html"
    image_path = "/admin/listing/images/custom-one.png"


class CustomTwo(AbstractBaseStyle):
    template_name = "listing/templatetags/custom_two.html"
    image_path = "/admin/listing/images/custom-two.png"


class CustomThree(AbstractBaseStyle):
    template_name = "listing/templatetags/custom_three.html"
    image_path = "/admin/listing/images/custom-three.png"


class CustomFour(AbstractBaseStyle):
    template_name = "listing/templatetags/custom_four.html"
    image_path = "/admin/listing/images/custom-four.png"


class CustomFive(AbstractBaseStyle):
    template_name = "listing/templatetags/custom_five.html"
    image_path = "/admin/listing/images/custom-five.png"


LISTING_CLASSES = []
LISTING_MAP = {}
for klass in (Horizontal, Vertical, Promo, VerticalThumbnail, Widget):
    LISTING_CLASSES.append(klass)
    LISTING_MAP[klass.__name__] = klass
for app in settings.INSTALLED_APPS:
    if app == "listing":
        continue
    try:
        mod = import_module(app + ".listing_styles")
    except ImportError:
        pass
    else:
        for name, klass in inspect.getmembers(mod, inspect.isclass):
            if name != "AbstractBaseStyle":
                LISTING_CLASSES.append(klass)
                LISTING_MAP[klass.__name__] = klass
for klass in (CustomOne, CustomTwo, CustomThree, CustomFour, CustomFive):
    LISTING_CLASSES.append(klass)
    LISTING_MAP[klass.__name__] = klass
