#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functools
import json
import logging

from kafka import KafkaProducer
from py_zipkin.thread_local import get_zipkin_attrs
from py_zipkin.thrift import zipkin_core
from thriftpy.protocol.binary import TBinaryProtocol
from thriftpy.transport import TMemoryBuffer
from py_zipkin.zipkin import zipkin_span, ZipkinAttrs, create_http_headers_for_new_span

'''
初始化
bootstrap_servers=['1.1.1.1:1234']
'''


def init_service(name, bootstrap_servers, port=None, topic_name="kuaizhan_zipkin", log_span_enabled=False, retries=3):
    global service_name
    service_name = name
    global producer
    producer = KafkaProducer(bootstrap_servers=bootstrap_servers, retries=retries)
    global topic
    topic = topic_name
    global log_span
    log_span = log_span_enabled
    global endpoint_port
    endpoint_port = port


'''
'''


def long_to_hex(num):
    return format(num & 0xffffffffffffffff, "x")


def add_result_to_binary_annotation(zipkin_context, result):
    try:
        zipkin_context.update_binary_annotations({"result": str(result)})
    except Exception:
        pass


'''
向kafka里面发送Json序列化的Span信息
'''


def transport_handler(message):
    transport_in = TMemoryBuffer(message)
    protocol_in = TBinaryProtocol(transport_in)
    span = zipkin_core.Span()
    span.read(protocol_in)
    if span.trace_id:
        span.trace_id = long_to_hex(span.trace_id)
    if span.parent_id:
        span.parent_id = long_to_hex(span.parent_id)
    if span.id:
        span.id = long_to_hex(span.id)
    for annotation in span.annotations:
        annotation['endpoint'] = annotation.pop('host')
    for binary_annotation in span.binary_annotations:
        binary_annotation['endpoint'] = binary_annotation.pop('host')
    message = json.dumps(span, default=lambda x: x.__dict__)
    producer.send(topic, message)
    if log_span:
        logging.info("zipkin message {}", message)


'''
tornador handler 装饰器
'''


def tornado_handler_dec():
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)):
                setattr(cls, attr, http_root_span(getattr(cls, attr)))
        return cls

    return decorate


'''
tornado handler 方法装饰器
'''


def http_root_span(func):
    @functools.wraps(func)
    def wapper(handler, *args, **kw):
        headers = handler.request.headers
        zipkin_attrs = ZipkinAttrs(
            trace_id=headers.get('X-B3-TraceID', None),
            span_id=headers.get('X-B3-SpanID', None),
            parent_span_id=headers.get('X-B3-ParentSpanID', None),
            flags=headers.get('X-B3-Flags', None),
            is_sampled=headers.get('X-B3-Sampled', None),
        )
        existing_zipkin_attrs = get_zipkin_attrs()
        if existing_zipkin_attrs:
            with zipkin_span(
                    service_name=service_name,
                    span_name=handler.__class__.__name__ + "." + func.__name__,
            ) as zipkin_context:
                result = func(handler, *args, **kw)
                zipkin_context.update_binary_annotations({'status_code': handler.get_status()})
                add_result_to_binary_annotation(zipkin_context, result)
                return result
        else:
            with zipkin_span(
                    service_name=service_name,
                    zipkin_attrs=zipkin_attrs if zipkin_attrs[0] else None,
                    span_name=handler.__class__.__name__ + "." + func.__name__,
                    transport_handler=transport_handler,
                    report_root_timestamp=True,
                    port=endpoint_port if endpoint_port else 0,
                    sample_rate=100,  # 0.05, # Value between 0.0 and 100.0
            ) as zipkin_context:
                result = func(handler, *args, **kw)
                zipkin_context.update_binary_annotations({'status_code': handler.get_status()})
                add_result_to_binary_annotation(zipkin_context, result)
                return result

    return wapper


'''
普通方法装饰器
'''


def none_root_span(func):
    @functools.wraps(func)
    def wapper(*args, **kw):
        with zipkin_span(
                service_name=service_name,
                span_name=func.__name__,
        ) as zipkin_context:
            result = func(*args, **kw)
            add_result_to_binary_annotation(zipkin_context, result)
            return result

    return wapper


'''
grpc 服务类装饰器
'''


def grpc_service_dec():
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)):
                setattr(cls, attr, grpc_root_span(getattr(cls, attr)))
        return cls

    return decorate


'''
grpc 方法装饰器
'''


def grpc_root_span(func):
    @functools.wraps(func)
    def wapper(service, request, context):
        metadata = context.invocation_metadata()
        zipkin_attrs = None
        if len(metadata) == 6:
            zipkin_attrs = ZipkinAttrs(
                trace_id=metadata[0][0],
                span_id=metadata[1][0],
                parent_span_id=metadata[2][0],
                flags=metadata[3][0],
                is_sampled=metadata[4][0],
            )
        existing_zipkin_attrs = get_zipkin_attrs()
        if existing_zipkin_attrs:
            with zipkin_span(
                    service_name=service_name,
                    span_name=func.__name__,
            ) as zipkin_context:
                result = func(service, request, context)
                add_result_to_binary_annotation(zipkin_context, result)
                return result
        else:
            with zipkin_span(
                    service_name=service_name,
                    zipkin_attrs=zipkin_attrs if zipkin_attrs else None,
                    span_name=func.__name__,
                    transport_handler=transport_handler,
                    port=endpoint_port if endpoint_port else 0,
                    report_root_timestamp=True,
                    sample_rate=100,  # 0.05, # Value between 0.0 and 100.0
            ) as zipkin_context:
                result = func(service, request, context)
                add_result_to_binary_annotation(zipkin_context, result)
                return result

    return wapper


'''
grpc client 调用服务的时候传递metadata
'''


def get_grpc_metadata():
    span = create_http_headers_for_new_span()
    properties = ['X-B3-TraceId',
                  'X-B3-SpanId',
                  'X-B3-ParentSpanId',
                  'X-B3-Flags',
                  'X-B3-Sampled']
    tuple = ((span.get(i), i) for i in properties)
    return tuple


'''
http rpc的时候传递http header
'''


def get_http_header():
    return create_http_headers_for_new_span()
