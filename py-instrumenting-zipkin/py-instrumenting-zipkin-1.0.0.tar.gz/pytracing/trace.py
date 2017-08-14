import json

from django.conf import settings

from py_zipkin.zipkin import zipkin_span
from py_zipkin.zipkin import create_attrs_for_span
from py_zipkin.zipkin import ZipkinAttrs
from py_zipkin.util import generate_random_64bit_string
from py_zipkin.util import generate_random_128bit_string

from .transporter import transport_handler
from . import constants


class Trace(object):

    zipkin_context = None
    extras = {}

    def __init__(self):
        self.request = None
        self.operation_name = None
        self.extras = {}

    def __get_request_headers(self):
        headers = {}

        for k, v in self.request.META.iteritems():
            if k.startswith('HTTP'):
                headers[k] = v
        return headers

    def __get_host(self):
        return self.request.META[constants.REMOTE_ADDR]

    def __get_port(self):
        return int(self.request.META[constants.SERVER_PORT])

    def __get_query_params(self):
        return self.request.META.get(constants.QUERY_STRING)

    def __get_uri(self):
        return self.request.META[constants.PATH_INFO]

    def __get_parent_span_id(self):
        return self.request.META.get(
            constants.HTTP_X_B3_PARENTSPANID, None)

    def __get_trace_id(self):
        return self.request.META.get(
            constants.HTTP_X_B3_TRACEID, None)

    def __get_flags(self):
        return self.request.META.get(
            constants.HTTP_X_B3_FLAGS, '0')

    def __is_sampled(self):
        return self.request.META.get(
            constants.IS_SAMPLED, 'false') == 'true',

    def __get_span_attrs(self, use_128bit_trace_id=False):
        parent_span_id = self.__get_parent_span_id()
        trace_id = self.__get_trace_id()

        if trace_id is None:
            if use_128bit_trace_id:
                trace_id = generate_random_128bit_string()
            else:
                trace_id = generate_random_64bit_string()

        is_sampled = self.__is_sampled()
        span_id = generate_random_64bit_string()

        return ZipkinAttrs(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=parent_span_id,
                flags=self.__get_flags(),
                is_sampled=is_sampled,
        )

    def __operation_name(self):
        operation_name = self.__get_uri()
        return operation_name

    def start(self, request, operation_name=None, *args, **kwargs):
        self.request = request

        if not operation_name:
            operation_name = self.__operation_name()

        attrs = self.__get_span_attrs(self.request)
        context = zipkin_span(
            service_name=settings.ZIPKIN_SERVICE_NAME,
            span_name=operation_name,
            zipkin_attrs=attrs,
            transport_handler=transport_handler,
            host=self.__get_host(),
            port=self.__get_port(),
            sample_rate=settings.ZIPKIN_SAMPLE_RATE
        )
        self.zipkin_context = context

    def set_operation_details(self, view_func, view_args, view_kwargs):
        if hasattr(view_func, 'func_name'):
            self.extras.update(**{
                constants.ANNOTATION_DJANGO_VIEW_FUNC_NAME: (
                    view_func.func_name)}
            )

        if hasattr(view_func, 'im_class'):
            self.extras.update(**{
                constants.ANNOTATION_DJANGO_VIEW_CLASS: (
                    view_func.im_class.__name__)}
            )

        if hasattr(view_func, 'im_func'):
            self.extras.update(**{
                constants.ANNOTATION_DJANGO_VIEW_FUNC_NAME: (
                    view_func.im_func.func_name)}
            )

        self.extras.update(**{
            constants.ANNOTATION_DJANGO_VIEW_ARGS: json.dumps(view_args)})

        self.extras.update(**{
            constants.ANNOTATION_DJANGO_VIEW_KWARGS: json.dumps(view_kwargs)})

    def finish(self, response):
        if not self.zipkin_context:
            return

        with self.zipkin_context:
            self.zipkin_context.update_binary_annotations({
                constants.ANNOTATION_HTTP_URI: self.__get_uri(),
                constants.ANNOTATION_HTTP_HOST: self.__get_host(),
                constants.ANNOTATION_HTTP_HEADERS: self.__get_request_headers(),
                constants.ANNOTATION_HTTP_QUERY: self.__get_query_params(),
                constants.ANNOTATION_HTTP_STATUSCODE: response.status_code,
            })
            self.zipkin_context.update_binary_annotations(self.extras)
            return
