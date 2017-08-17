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

)

new_test = "class Test{view_name}(TestCase):\n"

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
        self.test_file_data = ""
        super(PostRecordTestGenerator, self).__init__(*args, **kwargs)

    def init_test(self, app_name):
        if not app_exists(app_name):
            raise Exception("can't find {0} app {1}".format(app_name,
                                                            'in {0}'.format(
                                                                get_app_path(app_name) if settings.DEBUG else "")))
        self.view_name = str(self.__class__.__name__)
        file_name, data = get_tests_file(app_name, file_name='tests.py')
        import_line = "from auto_generated_tests.py import *\n"
        if import_line not in data:
            with open(file_name, 'a') as file:
                file.seek(0)
                file.write(import_line)

        self.tests_file, self.test_file_data = get_tests_file(app_name, data=global_template.format(app_name=app_name,
                                                                                                    view_name=self.view_name))
        # self.test_app = (
        #                  new_test.format(view_name=self.view_name) + "{functions}")

    def post(self, request):

        if not self.view_name or not self.tests_file:
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

        self.append_to_test(data=data, action=action, request=request, pk=pk)

    def append_to_test(self, data, action, request, pk):
        class_declaration = new_test.format(view_name=self.view_name)
        index = self.test_file_data.find(class_declaration)

        # new test
        if index == -1:

            with open(self.tests_file, 'a') as file:
                file.write(class_declaration + functions_template.format(action=action,
                                                                         result=data.data,
                                                                         view_name=self.view_name,
                                                                         request_data=request.data,
                                                                         request_user_pk=pk))

        else:
            with open(self.tests_file, 'a+') as file:
                seek = 0
                for i, line in enumerate(file):
                    if class_declaration == line:
                        seek = i + 1
                        break

                file.seek(seek)
                file.write(functions_template.format(action=action,
                                                     result=data.data,
                                                     view_name=self.view_name,
                                                     request_data=request.data,
                                                     request_user_pk=pk))
