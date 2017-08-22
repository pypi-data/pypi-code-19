import os

from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import TestCase
from django.test.client import Client, RequestFactory

from category.models import Category, Tag

from listing.models import Listing
from listing.styles import LISTING_CLASSES
from listing.tests.models import ModelA, ModelB


RES_DIR = os.path.join(os.path.dirname(__file__), "res")
IMAGE_PATH = os.path.join(RES_DIR, "image.jpg")


def set_image(obj):
    obj.image.save(
        os.path.basename(IMAGE_PATH),
        ContentFile(open(IMAGE_PATH, "rb").read())
    )


class ModelsTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

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

        obj = Category.objects.create(title="CatB", slug="cat-b")
        cls.cat_b = obj

        obj = Tag.objects.create(title="TagA", slug="tag-a")
        cls.tag_a = obj

        obj = Tag.objects.create(title="TagB", slug="tag-b")
        cls.tag_b = obj

        obj = ModelA.objects.create(title="ModelA", slug="model-a")
        obj.categories = [cls.cat_a]
        obj.tags = [cls.tag_a]
        obj.save()
        cls.model_a = obj

        obj = ModelB.objects.create(title="ModelB", slug="model-b")
        obj.categories = [cls.cat_b]
        obj.tags = [cls.tag_b]
        obj.save()
        cls.model_b = obj

        obj = ModelA.objects.create(title="ModelA Published", slug="model-a-p")
        obj.categories = [cls.cat_a]
        obj.tags = [cls.tag_a]
        obj.sites = Site.objects.all()
        obj.publish()
        cls.model_a_published = obj

        obj = ModelB.objects.create(title="ModelB Published", slug="model-b-p")
        obj.categories = [cls.cat_b]
        obj.tags = [cls.tag_b]
        obj.sites = Site.objects.all()
        obj.publish()
        cls.model_b_published = obj

    def test_content_types(self):
        listing = Listing.objects.create()
        listing.content_types = [ContentType.objects.get_for_model(ModelA)]
        listing.save()
        qs = listing.queryset
        self.assertEqual(len(qs), 2)
        self.failUnless(self.model_a.modelbase_obj in qs)

    def test_content_types_permitted(self):
        listing = Listing.objects.create()
        listing.content_types = [ContentType.objects.get_for_model(ModelA)]
        listing.save()
        qs = listing.queryset_permitted
        self.assertEqual(len(qs), 1)
        self.failUnless(self.model_a_published.modelbase_obj in qs)

    def test_content(self):
        listing = Listing.objects.create()
        listing.set_content([self.model_a, self.model_a_published])
        qs = listing.queryset
        self.assertEqual(len(qs), 2)
        self.failUnless(self.model_a.modelbase_obj in qs)
        qs = listing.content_queryset
        self.assertEqual(len(qs), 2)
        self.failUnless(self.model_a.modelbase_obj in qs)

    def test_content_permitted(self):
        listing = Listing.objects.create()
        listing.set_content([self.model_a, self.model_a_published])
        qs = listing.queryset_permitted
        self.assertEqual(len(qs), 1)
        self.failUnless(self.model_a_published.modelbase_obj in qs)
        qs = listing.content_queryset_permitted
        self.assertEqual(len(qs), 1)
        self.failUnless(self.model_a_published.modelbase_obj in qs)

    def test_pinned(self):
        listing = Listing.objects.create()
        listing.set_pinned([self.model_a, self.model_a_published])
        qs = listing.pinned_queryset
        self.assertEqual(len(qs), 2)
        self.failUnless(self.model_a.modelbase_obj in qs)

    def test_pinned_permitted(self):
        listing = Listing.objects.create()
        listing.set_pinned([self.model_a, self.model_a_published])
        qs = listing.pinned_queryset_permitted
        self.assertEqual(len(qs), 1)
        self.failUnless(self.model_a_published.modelbase_obj in qs)

    def test_content_with_pinned(self):
        """Pinned content is excluded from queryset"""
        listing = Listing.objects.create()
        listing.set_content([self.model_a, self.model_a_published])
        listing.set_pinned([self.model_a])
        qs = listing.queryset
        self.assertEqual(len(qs), 1)
        self.failIf(self.model_a.modelbase_obj in qs)

    def test_categories(self):
        listing = Listing.objects.create()
        listing.categories = [self.cat_a]
        listing.save()
        qs = listing.queryset
        self.assertEqual(len(qs), 2)
        self.failUnless(self.model_a.modelbase_obj in qs)

    def test_categories_permitted(self):
        listing = Listing.objects.create()
        listing.categories = [self.cat_a]
        listing.save()
        qs = listing.queryset_permitted
        self.assertEqual(len(qs), 1)
        self.failUnless(self.model_a_published.modelbase_obj in qs)

    def test_tags(self):
        listing = Listing.objects.create()
        listing.tags = [self.tag_a]
        listing.save()
        qs = listing.queryset
        self.assertEqual(len(qs), 2)
        self.failUnless(self.model_a.modelbase_obj in qs)

    def test_tags_permitted(self):
        listing = Listing.objects.create()
        listing.tags = [self.tag_a]
        listing.save()
        qs = listing.queryset_permitted
        self.assertEqual(len(qs), 1)
        self.failUnless(self.model_a_published.modelbase_obj in qs)

    def test_logical_and(self):
        listing = Listing.objects.create()
        listing.content_types = [ContentType.objects.get_for_model(ModelA)]
        listing.categories = [self.cat_a]
        listing.tags = [self.tag_a]
        listing.save()
        qs = listing.queryset
        self.assertEqual(len(qs), 2)
        self.failUnless(self.model_a.modelbase_obj in qs)

    def test_logical_and_permitted(self):
        listing = Listing.objects.create()
        listing.content_types = [ContentType.objects.get_for_model(ModelA)]
        listing.categories = [self.cat_a]
        listing.tags = [self.tag_a]
        listing.save()
        qs = listing.queryset_permitted
        self.assertEqual(len(qs), 1)
        self.failUnless(self.model_a_published.modelbase_obj in qs)

    def test_iter(self):
        listing = Listing.objects.create()
        listing.content_types = [ContentType.objects.get_for_model(ModelA)]
        listing.save()
        self.assertEqual(len(listing), 1)
        self.failUnless(self.model_a_published.modelbase_obj in listing)

    def test_slug_uniqueness(self):
        sites = Site.objects.all()
        listing = Listing.objects.create(title="tsu", slug="tsu")
        listing.sites = [sites[0]]
        listing.save()
        listing = Listing.objects.create(title="tsu", slug="tsu")
        with self.assertRaises(RuntimeError):
            listing.sites = [sites[0]]
