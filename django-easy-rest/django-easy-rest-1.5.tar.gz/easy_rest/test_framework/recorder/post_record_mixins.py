from datetime import datetime
from ..resolvers.resolve import get_tests_file, app_exists, get_app_path, in_test
from ..resolvers.settings import get_override_settings
from django.conf import settings

global_template = (
    "from django.test import TestCase\n"
    "from {app_name}.views import {view_name}\n"
    "from django.test import RequestFactory\n"
    "from django.contrib.auth.models import AnonymousUser, User\n"
    "from easy_rest.test_framework.resolvers.resolve import register_unitest\n"
    "from django.test.utils import override_settings\n\n"  # pep 8
    "register_unitest()\n\n\n"  # pep8
    "def resolve_user(pk):\n"
    "    try:\n"
    "        return User.objects.get(pk=pk)\n"
    "    except Exception:\n"
    "        return AnonymousUser()\n"
    "\n\n"  # pep8

)

new_test = ("class Test{view_name}(TestCase):\n"
            "    def __init__(self, *args, **kwargs):\n"
            "        super(TestApiTest, self).__init__(*args, **kwargs)\n"
            "        self.test = {view_name}()\n"
            "\n")  # pep 8

functions_template = (
    "    @override_settings({override_settings})\n"
    "    def test_{action}(self):\n"
    "        request = RequestFactory()\n"
    "        request.data = {request_data}\n"
    "        request.user = resolve_user({request_user_pk})\n"
    "        result = {result}\n"
    "        if type(result) is dict:\n"
    "            return self.assertDictEqual(result, self.test.post(request).data)\n"
    "        return self.assertEqual(result, self.test.post(request).data)\n"
    "\n"  # pep 8
)


class PostRecordTestGenerator(object):
    def __init__(self, *args, **kwargs):
        """
        this just sets the class to initialize view_name, test_File, current_settings_keys,
        test_file_data, test_file_name to defaults
        :param args:
        :param kwargs:
        """
        # the name of the view to test
        self.view_name = None
        # the file to write test to
        self.tests_file = None
        # the settings to keep in the test
        # for example when testing keep debug as it was when recorded
        self.use_current_settings_keys = ['DEBUG']
        # the test file data
        self.test_file_data = ""
        # the test file name
        self.test_file_name = 'auto_generated_post_record_test'
        super(PostRecordTestGenerator, self).__init__(*args, **kwargs)

    def init_test(self, app_name):
        """
        this function initializes the test
        :param app_name: the app to test
        :return: None
        """

        # checking if the app exists if not raises an exception
        if not app_exists(app_name):
            raise Exception("can't find {0} app {1}".format(app_name,
                                                            'in {0}'.format(
                                                                get_app_path(app_name) if settings.DEBUG else "")))
        # getting the view to test
        self.view_name = str(self.__class__.__name__)

        # the test file , data it contained
        file_name, data = get_tests_file(app_name, file_name='tests.py')

        # the line to import
        import_line = "from .{} import *\n".format(self.test_file_name)
        # checking if import line is in data
        # if not appending import line to data. (global test file)
        if import_line not in data:
            with open(file_name, 'a') as file:
                file.seek(0)
                file.write(import_line)

        # generating or reading specific test file
        self.tests_file, self.test_file_data = get_tests_file(app_name, data=global_template.format(app_name=app_name,
                                                                                                    view_name=self.view_name),
                                                              file_name='auto_generated_post_record_test.py')

    def post(self, request):
        """
        Overriding the original post function
        :param request: WSGI request
        :return: rest_framework.Response
        """

        # if this is a test post (Mocked post)
        if in_test():
            # does nothing
            return super(PostRecordTestGenerator, self).post(request)

        # if the were an error upon initialization
        if not self.view_name or not self.tests_file:
            raise Exception("unsuccessful init maybe you forgot calling init_test ?")

        # trying to get the action of the current request
        try:
            # getting the requested action
            action = self._pythonize(request.data[self.function_field_name])
        except Exception:
            # if the is not action generating new test name
            action = 'easy_rest_{}_test'.format(self.function_from_time())

        # getting the data if the post response
        data = super(PostRecordTestGenerator, self).post(request)

        # try getting the pk of the post user
        pk = request.user.pk

        # appending data to the test
        self.append_to_test(data=data, action=action, request=request, pk=pk)

        # returning the original data
        return data

    def append_to_test(self, data, action, request, pk):
        """
        Appending a new test or to original test
        :param data: data of post
        :param action: action of request
        :param request: WSGI request
        :param pk: user pk
        :return: None
        """
        # generating the class declaration for the test
        class_declaration = 'class Test{view_name}(TestCase):\n'.format(view_name=self.view_name)
        # class full declaration including init
        class_declaration_full = new_test.format(view_name=self.view_name)
        # setting index to point to the beginning of the class file (FP)
        index = self.test_file_data.find(class_declaration)

        # if class was not found (FP = -1)
        if index == -1:
            with open(self.tests_file, 'a') as file:
                # appending class declaration + generated test
                file.write(
                    class_declaration_full + self.format_function(name=action, data=data, request=request, pk=pk))
        # if class existed in test file
        else:

            # the start of the test before the current test
            start = ""
            # the name of the function
            function_name = "test_{action}".format(action=action)
            # prefix to append to the function name
            prefix = ""
            # the end of the test class
            end = ""

            # boolean holds if before class declaration
            before_declaration = True

            # iterating over the current test file
            with open(self.tests_file, 'r') as file_read:
                for i, line in enumerate(file_read):
                    if before_declaration:  # if current line is class declaration
                        start += line
                    else:
                        end += line  # if current line is after class declaration
                    if function_name in line:  # if a function with that name exists
                        prefix = action

                    # after declaration
                    if line == class_declaration:
                        before_declaration = False
            # generating test name or using original depends if it existed
            name = action if not prefix else self.function_from_time(prefix=prefix)

            # writing the current test
            with open(self.tests_file, 'w+') as file:
                file.write(start + self.format_function(name=name, data=data, request=request, pk=pk) + end)

    def format_function(self, name, data, request, pk):
        """
        Formatting a new test
        :param name: test name
        :param data: data of post
        :param request: WSGI request
        :param pk: user pk
        :return: new formatted test
        """
        return functions_template.format(action=name,
                                         result=data.data,
                                         request_data=request.data,
                                         request_user_pk=pk,
                                         override_settings=get_override_settings(
                                             attributes=self.use_current_settings_keys
                                         ))

    @staticmethod
    def function_from_time(prefix="", suffix=""):
        """
        Generates a new function name from time
        :param prefix: prefix to append
        :param suffix: suffix to append
        :return: new function name (str)
        """
        return prefix + ("_" if prefix else "") + str(datetime.now()).replace(
            ':', "_"
        ).replace(".", "_").replace("-", "_").replace(" ", "_") + ("_" if suffix else "") + suffix
