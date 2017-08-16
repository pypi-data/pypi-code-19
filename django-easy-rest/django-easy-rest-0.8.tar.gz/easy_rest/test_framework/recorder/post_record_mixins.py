from datetime import datetime
from ..resolvers.resolve import get_tests_file, app_exists, get_app_path
from django.conf import settings

global_template = (
    "from unittest import TestCase\n"
    "from {app_name}.views import {view_name}\n"
    "from django.test import RequestFactory\n"
    "from django.contrib.auth.models import AnonymousUser, User\n"
    "def resolve_user(pk):\n"
    "    try:\n"
    "        return User.objects.get(pk=pk)\n"
    "    except Exception:\n"
    "        return AnonymousUser()\n"
    "class Test{view_name}(TestCase):\n"

)

functions_template = (
    "    def test_{action}(self):\n"
    "        request=RequestFactory()\n"
    "        request.data = {request_data}\n"
    "        request.user = resolve_user({request_user_pk})\n"
    "        if type({result}) is dict:\n"
    "            return self.assertDictEqual({result}, {view_name}.post(request))\n"
    "        return self.assertEqual({result}, {view_name}.post(request))\n"
)


class PostRecordTestGenerator(object):
    def __init__(self, *args, **kwargs):
        self.view_name = None
        self.tests_file = None
        self.test_app = None
        self.functions = None
        super(PostRecordTestGenerator, self).__init__(*args, **kwargs)

    def init_test(self, app_name, view_name):
        if not app_exists(app_name):
            raise Exception("can't find {0} app {1}".format(app_name,
                                                            'in {0}'.format(
                                                                get_app_path(app_name) if settings.DEBUG else "")))
        self.view_name = view_name
        self.tests_file = get_tests_file(app_name)
        self.test_app = global_template.format(app_name=app_name, view_name=view_name) + "{functions}"
        self.functions = ""

    def post(self, request):

        if not self.view_name or not self.tests_file or not self.test_app:
            raise Exception("unsuccessful init did you miss calling init_test ?")
        try:
            # getting the requested action
            action = self._pythonize(request.data[self.function_field_name])
        except Exception:
            action = 'easy_rest_{}_test'.format(str(datetime.now()).replace(
                ':', "_"
            ).replace(".", "_").replace("-", "_").replace(" ", "_"))

        data = super(PostRecordTestGenerator, self).post(request)
        pk = request.user.pk
        self.functions += functions_template.format(action=action,
                                                    result=data.data,
                                                    view_name=self.view_name,
                                                    request_data=request.data,
                                                    request_user_pk=pk)
        with open(self.tests_file, 'w+') as file:
            file.write(self.test_app.format(functions=self.functions))

        return data
