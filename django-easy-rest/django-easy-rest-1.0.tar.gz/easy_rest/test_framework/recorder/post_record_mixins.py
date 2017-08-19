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
        self.test_file_name = 'auto_generated_post_record_test'
        super(PostRecordTestGenerator, self).__init__(*args, **kwargs)

    def init_test(self, app_name):
        if not app_exists(app_name):
            raise Exception("can't find {0} app {1}".format(app_name,
                                                            'in {0}'.format(
                                                                get_app_path(app_name) if settings.DEBUG else "")))
        self.view_name = str(self.__class__.__name__)
        file_name, data = get_tests_file(app_name, file_name='tests.py')
        import_line = "from auto_generated_post_record_test import *\n"
        if import_line not in data:
            with open(file_name, 'a') as file:
                file.seek(0)
                file.write(import_line)

        self.tests_file, self.test_file_data = get_tests_file(app_name, data=global_template.format(app_name=app_name,
                                                                                                    view_name=self.view_name),
                                                              file_name='auto_generated_post_record_test.py')
        # self.test_app = (
        #                  new_test.format(view_name=self.view_name) + "{functions}")

    def post(self, request):

        if not self.view_name or not self.tests_file:
            raise Exception("unsuccessful init did you miss calling init_test ?")
        try:
            # getting the requested action
            action = self._pythonize(request.data[self.function_field_name])
        except Exception:
            action = 'easy_rest_{}_test'.format(self.function_from_time())

        data = super(PostRecordTestGenerator, self).post(request)
        pk = request.user.pk

        self.append_to_test(data=data, action=action, request=request, pk=pk)

        return data

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
            start = ""
            function_name = "test_{action}".format(action=action)
            prefix = ""
            end = ""
            seek = 0
            with open(self.tests_file, 'r') as file_rad:
                for i, line in enumerate(file_rad):
                    # print(line.encode('utf-8'), class_declaration.encode('utf-8'))
                    if class_declaration == line:
                        seek = i
                    if not seek or seek == i:
                        start += line
                    else:
                        end += line
                    print(function_name, line, function_name in line)
                    if function_name in line:
                        prefix = action

            name = action if not prefix else self.function_from_time(prefix=prefix)
            with open(self.tests_file, 'w+') as file:
                file.write(start + functions_template.format(action=name,
                                                             result=data.data,
                                                             view_name=self.view_name,
                                                             request_data=request.data,
                                                             request_user_pk=pk) + end)

    @staticmethod
    def function_from_time(prefix="", suffix=""):
        return prefix + ("_" if prefix else "") + str(datetime.now()).replace(
            ':', "_"
        ).replace(".", "_").replace("-", "_").replace(" ", "_") + ("_" if suffix else "") + suffix
