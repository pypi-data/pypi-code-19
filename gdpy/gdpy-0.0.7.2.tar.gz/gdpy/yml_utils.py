# -*- coding:utf-8 -*-
from .utils import json_loader, json_dumper
import collections
import yaml
import sys

is_py2 = (sys.version_info[0] == 2)
is_py3 = (sys.version_info[0] == 3)

default_encoding = "utf-8"

if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding("utf-8")


def yaml_loader(file_name):
    with open(file_name, 'r') as f:
        return yaml.load(f.read())


def yaml_dumper(data):
    return yaml.safe_dump(data, default_flow_style=False, encoding=('utf-8'), allow_unicode=True)


if is_py2:
    def convert(data):
        if isinstance(data, basestring):
            return str(data).encode('utf-8')
        elif isinstance(data, collections.Mapping):
            return dict(map(convert, data.iteritems()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(convert, data))
        else:
            return data
elif is_py3:
    def convert(data):
        if isinstance(data, (str, bytes)):
            return data
        elif isinstance(data, collections.Mapping):
            return dict(map(convert, data.items()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(convert, data))
        else:
            return data


def parse_list_tasks(result, body):
    body = json_loader(body)
    result.task_list = convert(body).get('task_list')
    result.count = body.get('count', 0)
    result.total = body.get('total', 0)
    return result


def parse_get_jobs(result, body):
    body = json_loader(body)
    result.jobs = convert(body).get('jobs')
    result.count = len(result.jobs)
    return result


def parse_list_workflows(result, body):
    body = json_loader(body)
    result.workflows = convert(body).get('items')
    result.count = len(result.workflows)
    return result


def parse_list_tools(result, body):
    body = json_loader(body)
    result.tools = convert(body).get('items')
    result.count = len(result.tools)
    return result


def parse_get_tool_parameters(result, body):
    body = json_loader(body)
    result.parameters = convert(body).get('parameter')
    return result
