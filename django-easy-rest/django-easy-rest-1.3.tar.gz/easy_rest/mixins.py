from copy import copy
from django.views.decorators.csrf import csrf_exempt
from easy_rest.serializers import FullDebuggerSerializer
from django.http import HttpResponse
from easy_rest.utils.search_model import GetModelByString
import json
from django.conf import settings


class Resolver(object):
    """
    the resolver resolve attribute set, get and method calling
    this is used in order to have a nice clean code in ide.
    """

    def _get_value(self, name, default=None):
        """
        returns the variable value if exists else default
        :param name: the variable name
        :param default: default value
        :return: variable value if exists else default
        """
        if hasattr(self, name):
            return getattr(self, name)
        return default

    def _set_value(self, name, value):
        """
        settings a value of variable
        :param name: the variable name
        :param value: the value to set
        :return: True if succeeded else false
        :rtype: bool
        """
        if hasattr(self, name):
            setattr(self, name, value)
            return True
        return False

    def _call(self, name, **kwargs):
        """
        Calling a function
        :param name: function name
        :param kwargs: kwargs to use when calling
        :return: function output if there is one else None
        """
        if hasattr(self, name):
            return getattr(self, name)(**kwargs)


class FunctionUnPackerMixin(Resolver):
    """
    This mixin handles the unpacking of variables into functions

    Example: unpacks {'a':'value of a', 'b':'value of b'} results in function(a='value of a', b='value of b')
    """

    def prepare_function_data(self, data, method=None, append_data=None):
        """
        prepare data into a new dictionary
        :param data: data to prepare
        :param method: method the method latter to call
        :param append_data: append_data data to append at call
        :return: prepared data
        :rtype: dict
        """
        # packed if any data got packed
        packed = False
        # the prepared data
        prepared_data = {}
        # default value for append_data because default parameters should be runtime const
        append_data = append_data if append_data else {}

        # if method is none then can't prepare the parameters because there are no function argument
        if not method:
            prepared_data = {self._get_value("default_parameter", 'data'): data}
        else:
            # get function variable names.
            keys = list(method.__code__.co_varnames)
            # removing self from variables if self in variables because the call is self.call
            if 'self' in keys:
                keys.remove('self')
            # if there are no keys
            keys = [] if not keys else keys
            for key in keys:
                # if data has this key
                if key in data:
                    # then pack was successful
                    packed = True
                    # packing the variable
                    prepared_data[key] = data[key]
            # trying to set the first parameter to all data
            if not packed:
                prepared_data = {keys[0]: data}
        # update prepared data to append data
        prepared_data.update(append_data)
        # returning the prepared data.
        return prepared_data

    def call_method(self, data, method):
        """
        Calls the method with the prepared data
        :param data: prepared data
        :param method: method to call
        :return: method out put
        """
        return method(**self.prepare_function_data(data=data, method=method, append_data=None))


class HelpMixin(object):
    """
    Add help for the api methods
    All fields initialized after inheritance
    """
    general_help_string = 'for function summary use: {usage}'
    method_helpers = {'__all__': {"help": {"general": "this is a special message"}}}

    def __init__(self, *args, **kwargs):
        super(HelpMixin, self).__init__(*args, **kwargs)
        self.general_help_string.format(usage=self.get_general_function_help_usage())

    def get_general_function_help_usage(self, action=None):
        """
        this functions returns the general help message by the action
        :param action: action to return message using
        :return: help usage
        :rtype dict
        """
        # if there is no action
        action = "specific" + self.function_field_name if not action else action
        # creating help prefix
        help_prefix_string = self.restifiy('help prefix')
        return {self.function_field_name: action, help_prefix_string: "specific error"}

    def _method_wrapper(self, data, method, action):
        """
        the method wraper is used in order to wrap the method call
        :param data: request.data (dict)
        :param method: method to call inside api (object)
        :param action: action name (str)
        :return: function data, debug, error
        :rtype bool
        """
        # value of method out
        out = None
        # additional values
        additional = None
        # debug dictionary
        debug = {}

        # trying to call the method
        try:
            out = self.call_method(data=data, method=method)

        # excepting any exception when calling
        except Exception as error:
            # key is used to check if this method has helper are use global
            key = '__all__' if action not in self.method_helpers else action

            # if this method does have an helper
            if key in self.method_helpers:
                # the key of prefix
                help_prefix_string = self.restifiy('help prefix')
                # the prefix to use when searching default general
                help_prefix = data.get(help_prefix_string, 'general')
                # the returned help message
                help_message = {"message": self.method_helpers[key]['help'].get(help_prefix, 'help not found'),
                                'usage': 'specific help use {usage}'.format(
                                    usage=self.get_general_function_help_usage(action=action)),
                                self.restifiy('help list'): 'available help entries {helpers}'.format(
                                    helpers=self.method_helpers[key]['help'].keys())}
                # sets the additional text
                additional = {"help": help_message}
            else:
                # sets the additional text differently
                additional = {'error': "Exception occurred in method check function usage",
                              self.function_field_name: action}
            # adding debug info
            if settings.DEBUG:
                debug = {'exception-type': str(type(error)), 'exception-args': error.args}

        # deciding what to return
        if additional:
            return additional, debug, True
        if out:
            return out, debug, False
        # if there is no additional and no out.
        if settings.DEBUG:
            return {}, {"error": '{} did not return any data'.format(self.function_field_name)}, True


class DecorativeKeysMixin(object):
    """
    The decorative keys mixin make the rest api more usable with
    any key separation
    """

    # the decorative keys separator (default)
    separator = '-'

    # the allowed formats
    decorative_keys_formats = [' ', "-", ":"]

    def _pythonize(self, name):
        """
        make action/method name into python friendly variable.
        :param name: the original name
        :return: python friendly variable/method
        :rtype: str
        """
        for value in self.decorative_keys_formats:
            name = name.replace(value, "_")
        if self.separator in name:
            name = name.replace(self.separator, '_')
        return name.lower()

    def restifiy(self, data):
        """
        the restifiy method returns a current rest decorative key
        :param data: the data to create a key from
        :return: current rest key
        :rtype: str
        """
        for value in self.decorative_keys_formats:
            return data.replace(value, self.separator)
        if '_' in data:
            return data.replace('_', self.separator)


class ApiAbstractionsMixin(object):
    """
    the api abstraction mixin allowed to add api middle way abstractions
    """
    # all abstracted allowed methods
    api_abstraction_methods = ['__all__']

    # api methods and binds
    abstractions_bind = {}

    # the main abstraction method
    def api_abstractions(self, data):
        """
        get the request data and returns the processed data
        :param data: request data
        :return: processed data
        """

        # debug data is a copy of data
        debug_data = {} if not settings.DEBUG else copy(data)

        # check if an item is allowed in the api_abstraction_methods
        check = lambda item: True
        if '__all__' not in self.api_abstraction_methods:
            # testing the abstraction
            check = lambda item: self._pythonize(item) in self.api_abstraction_methods

        # iterating over all binded methods
        for key in self.abstractions_bind:
            # checking if method is allowed
            if check(key):
                # getting the real key
                real_key = self.restifiy(key)
                # if real key in data calling the binded function
                if real_key in data:
                    # making the call
                    data, debug_data = self.abstractions_bind[key](data=data, debug_data=debug_data, real_key=real_key)
        if settings.DEBUG:
            self.base_response['debug'][self.restifiy('processed data')] = debug_data
        return data


class ModelUnpacker(ApiAbstractionsMixin, FunctionUnPackerMixin):
    """
    unpacks a model into a function on post
    """

    def __init__(self, *args, **kwargs):
        super(ModelUnpacker, self).__init__(*args, **kwargs)
        # binding the main function into the command "with-model"
        self.abstractions_bind['with model'] = self.handle_get_model

    # the model resolver gets a model from app by name
    model_resolver = GetModelByString()

    # debug serializer is used for serializing the model on debug
    debug_serializer = FullDebuggerSerializer()

    def handle_get_model(self, data, real_key, debug_data):
        """
        returns the real model when processed
        :param data: the data before processing
        :param real_key: the key in data to refer to
        :param debug_data: the debug data to append to
        :return: processed data, debug_data
        """
        # get model supports many models checking if there are many models
        if type(data[real_key]) is not list:
            # converting the when item into list
            data[real_key] = [data[real_key]]
        # iterating over the models to get list
        for i in range(len(data[real_key])):
            # getting the model
            obj, debug_obj = self.get_model(**data[real_key][i])
            # saving the model primary key in request
            prm_key = list(obj.keys())[0]

            # if this pk in data
            if prm_key in data:
                # data in pk is real model
                data[prm_key] = [data[prm_key], obj[prm_key]]

                if settings.DEBUG:
                    # debug data is serialized model data
                    debug_data[prm_key] = [debug_data[prm_key], debug_obj[prm_key]]
            else:
                # many models
                data.update(obj)
                # many models
                debug_data.update(debug_obj)
        # removing old key
        del data[real_key]
        # removing old debug data
        del debug_data[real_key]
        # returning data
        return data, debug_data

    def get_model(self, query, field=None, model_name=None, app=None, split_by='.', name=None):
        """
        returns the model specified in function arguments
        :param query: the query to use when getting the model
        :param field: the filed to search by [App.ModelName]
        :param model_name: the model name
        :param app: the app to search in
        :param split_by: the parameter the splits the app and the model in field
        :param name: the model return name
        :return: real model
        """
        # if app is known
        if app:
            # returning the model by the app and model name and get it by query
            model = self.model_resolver.get_model(model_name=model_name, app=app).objects.get(**query)
            # if no returns name specified
            if not name:
                # returning by model name to lower
                name = model_name.lower()
            # returns the model
            return {name: model}, {name: self.debug_serializer.serialize(model)}
        else:
            # try handling field split
            try:
                app, model = field.split(split_by)
                return self.get_model(query=query, app=app, model_name=model, split_by=split_by, name=name)
            except ValueError:  # to many or not enough values to unpack
                return None, None


class FormPostMixin(Resolver):
    """
    this mixin supports django GCBV and make posts a rest api post
    """
    form_save_function = lambda form:form.save()

    def __init__(self, *args, **kwargs):
        super(FormPostMixin, self).__init__(*args, **kwargs)
        self.create_view_names = [
            "<class 'django.views.generic.edit.CreateView'>"
        ]

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(FormPostMixin, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        this is the generic rest api post
        :param request: the WSGI request object
        :param args: additional args
        :param kwargs: additional kwargs

        :return:
        """
        # class inheritance chain
        chain = [str(class_name) for class_name in self.__class__.__bases__]

        # checking for same values in lists
        if bool(set(chain) & set(self.create_view_names)):
            # sets the request object to none
            self.object = None
        else:
            # this raises an exception when there are no pk or slug.
            self.object = self.get_object()
        # getting the post form
        form = self.get_form()
        # if form was valid
        if form.is_valid():
            # creating the response object
            response = {"status": "post-success"}

            # if form should generate an alert trying to get the message
            success_message = self._get_value('success_message')

            # notifying client to alert
            if success_message:
                response['alert'] = {'type': 'success', 'message': success_message}
            # saving the form (the model)
            self.form_save_function(form)
        else:
            # handling error response
            response = {"status": "post-failure",
                        "form_cleaned_data": form.cleaned_data,
                        "form_errors": form.errors}
        # returning the http response
        return HttpResponse(json.dumps(response))
