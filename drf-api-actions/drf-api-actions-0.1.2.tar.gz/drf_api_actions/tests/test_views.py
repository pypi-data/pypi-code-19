import coreapi
import coreschema
from django.conf.urls import include, url
from django.test import TestCase, override_settings
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_api_actions.views import ActionReadMixin, SchemaGeneratorEx


class CommonTestView(APIView):
    def get(self, request):
        return Response('')


class ActionReadTestView(ActionReadMixin, CommonTestView):
    pass


class ExtraFieldsTestView(CommonTestView):
    extra_fields = (
        coreapi.Field(name='a', location='query', required=False,
                      schema=coreschema.String(description='description')),
    )


urlpatterns = [
    url('^action-read$', ActionReadTestView.as_view()),
    url('^extra-fields$', ExtraFieldsTestView.as_view()),
    url('^', include('drf_api_actions.urls'))
]


@override_settings(ROOT_URLCONF=__name__)
class BaseCoreAPITest(TestCase):
    def setUp(self):
        self.generator = SchemaGeneratorEx()
        self.schema = self.generator.get_schema()


class TestActionReadMixin(BaseCoreAPITest):
    def test_action_read(self):
        self.assertIsNone(self.schema['action-read'].get('list'))
        self.assertIsNotNone(self.schema['action-read'].get('read'))


class TestSchemaGeneratorEx(BaseCoreAPITest):
    def test_extra_fields(self):
        link = self.generator.get_link('common', 'list', ExtraFieldsTestView())
        self.assertEqual(link.fields, ExtraFieldsTestView.extra_fields, '能识别fields')
