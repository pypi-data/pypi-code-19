import os
import json

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase

from rest_framework.test import APIClient
from category.models import Category, Tag
from jmbo.models import ModelBase

from listing.models import Listing
from listing.tests.models import ModelA, ModelB


class APITestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()

        # Editor
        cls.editor = get_user_model().objects.create(
            username="editor-api",
            email="editor-api@test.com",
            is_superuser=True,
            is_staff=True
        )
        cls.editor.set_password("password")
        cls.editor.save()

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

        cls.listing = Listing.objects.create(title="listing", slug="listing")
        cls.listing.set_content([cls.model_a, cls.model_a_published])

    def setUp(self):
        self.client.logout()

    def login(self):
        self.client.login(username="editor-api", password="password")

    def test_listing_create(self):
        self.login()
        data = {
            "title": "title",
            "slug": "title",
            "style": "Vertical",
            "content": [
                {
                    "modelbase_obj": "http://testserver/api/v1/jmbo-modelbase/%s/" % self.model_a.pk,
                    "position": 0,
                }
            ]
        }
        # The content field leads to mangling of the form data. Avoid by
        # forcing JSON content type.
        response = self.client.post(
            "/api/v1/listing-listing/",
            json.dumps(data),
            content_type="application/json"
        )
        as_json = json.loads(response.content)
        self.assertTrue(Listing.objects.filter(slug="title").exists())
        listing = Listing.objects.get(slug="title")
        self.failUnless(self.model_a.modelbase_obj in listing.queryset)

    def test_listing_patch(self):
        self.login()
        data = {
            "content": [
                {
                    "modelbase_obj": "http://testserver/api/v1/jmbo-modelbase/%s/" % self.model_b.pk,
                    "position": 0,
                }
            ]
        }
        response = self.client.patch(
            "/api/v1/listing-listing/%s/" % self.listing.pk,
            json.dumps(data),
            content_type="application/json"
        )
        as_json = json.loads(response.content)
        listing = Listing.objects.get(slug="listing")
        self.failUnless(self.model_b.modelbase_obj in listing.queryset)
        self.failIf(self.model_a.modelbase_obj in listing.queryset)

    def test_listing_content(self):
        response = self.client.get(
            "/api/v1/listing-listing/%s/" % self.listing.pk
        )
        as_json = json.loads(response.content)
        self.failUnless(
            "http://testserver/api/v1/jmbo-modelbase/%s/" % \
                self.model_a.pk in as_json["content"]
        )
        self.failUnless(
            "http://testserver/api/v1/jmbo-modelbase/%s/" % \
                self.model_a_published.pk in as_json["content"]
        )

    def test_listing_queryset_objects(self):
        response = self.client.get(
            "/api/v1/listing-listing/%s/queryset_objects/" % self.listing.pk
        )
        as_json = json.loads(response.content)
        self.failUnless(
            "http://testserver/api/v1/jmbo-modelbase/%s/" % \
                self.model_a.pk in as_json
        )
        self.failUnless(
            "http://testserver/api/v1/jmbo-modelbase/%s/" % \
                self.model_a_published.pk in as_json
        )
