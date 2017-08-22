import os

from django import template
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import TestCase
from django.test.client import Client, RequestFactory

from category.models import Category

from listing.models import Listing
from listing.tests.models import ModelA


RES_DIR = os.path.join(os.path.dirname(__file__), "res")
IMAGE_PATH = os.path.join(RES_DIR, "image.jpg")


def set_image(obj):
    obj.image.save(
        os.path.basename(IMAGE_PATH),
        ContentFile(open(IMAGE_PATH, "rb").read())
    )


class TemplateTagsTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(TemplateTagsTestCase, cls).setUpTestData()
        cls.client = Client()
        cls.request = RequestFactory()
        cls.request.method = "GET"
        cls.request._path = "/"
        cls.request.get_full_path = lambda: cls.request._path

        # Editor
        cls.editor = get_user_model().objects.create(
            username="editor",
            email="editor@test.com",
            is_superuser=True,
            is_staff=True
        )
        cls.editor.set_password("password")
        cls.editor.save()
        cls.client.login(username="editor", password="password")

        obj = Category.objects.create(title="CatA", slug="cat-a")
        cls.cat_a = obj

        obj = ModelA.objects.create(title="ModelA Published", slug="model-a-p")
        obj.categories = [cls.cat_a]
        obj.sites = Site.objects.all()
        obj.publish()
        cls.model_a_published = obj

    def common(self, style, category=False):
        l = style.lower()
        listing = Listing.objects.create(slug="listing-%s" % l, style=style)
        listing.content_types = [ContentType.objects.get_for_model(ModelA)]
        listing.save()
        t = template.Template("{% load listing_tags %}{% listing 'listing-"
            + l
            + "' %}"
        )
        result = t.render(template.Context({"request": self.request}))
        self.failUnless("ModelA Published" in result)
        if category:
            self.failUnless("CatA" in result)

    def test_listing_vertical(self):
        self.common("Vertical", category=True)

    def test_listing_vertical_thumbnail(self):
        self.common("VerticalThumbnail", category=True)

    def test_listing_horizontal(self):
        self.common("Horizontal")

    def test_listing_promo(self):
        self.common("Promo")
