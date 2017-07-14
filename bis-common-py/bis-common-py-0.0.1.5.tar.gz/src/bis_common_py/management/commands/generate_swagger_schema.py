# coding: utf-8
import json

from django.core.management.base import BaseCommand
from rest_framework.schemas import get_schema_view
from rest_framework.test import APIRequestFactory
from rest_framework_swagger.renderers import OpenAPIRenderer


class Command(BaseCommand):
    help = 'Generate swagger schema'

    def handle(self, *args, **options):
        factory = APIRequestFactory()
        request = factory.get('/', {'format': 'openapi'})
        view = get_schema_view(
            renderer_classes=[OpenAPIRenderer]
        )
        raw_content = view(request).render().content
        content = json.dumps(json.loads(raw_content), indent=4)
        with open('swagger.schema', 'wb') as f:
            f.write(content)