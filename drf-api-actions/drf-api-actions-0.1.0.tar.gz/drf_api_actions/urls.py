from django.conf.urls import url
from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view

from drf_api_actions.renderers import ApiJsRenderer
from drf_api_actions.views import SchemaGeneratorEx

urlpatterns = [
    url('^docs/', include_docs_urls(title="API", generator_class=SchemaGeneratorEx)),
    url('^schema/', get_schema_view('API', generator_class=SchemaGeneratorEx)),
    url('^api.js', get_schema_view('API', generator_class=SchemaGeneratorEx, renderer_classes=[ApiJsRenderer])),
]
