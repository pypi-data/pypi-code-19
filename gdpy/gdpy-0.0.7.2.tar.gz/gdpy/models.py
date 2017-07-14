# -*- coding:utf-8 -*-

import json
from .compat import to_string
from .utils import *

"""
gdpy.models
该模块包含Python SDK API接口所需要的返回值类型。
"""


def _hget(headers, key, converter=lambda x: x):
    if key in headers:
        return converter(headers[key])
    else:
        return None


def _bget(body, key, converter=lambda x: x):
    body = json.loads(body)
    if key in body:
        return converter(body[key])
    else:
        return None


class RequestResult(object):
    def __init__(self, resp):
        #: HTTP response
        self.response = resp.response
        #: HTTP status code
        self.status = resp.status
        #: HTTP headers
        self.headers = resp.headers
        #: HTTP read
        self.read = resp.read


class ListTasksResult(RequestResult):
    def __init__(self, resp):
        super(ListTasksResult, self).__init__(resp)
        # tasks 列表
        self.task_list = []
        # tasks 计数
        self.count = 0
        # tasks 总数
        self.total = 0


class GetTaskResult(RequestResult):
    def __init__(self, resp):
        super(GetTaskResult, self).__init__(resp)


class GetJobResult(RequestResult):
    def __init__(self, resp):
        super(GetJobResult, self).__init__(resp)
        # jobs 列表
        self.jobs = []
        # jobs 计数
        self.count = 0


class GetJobCmdResult(RequestResult):
    def __init__(self, resp):
        super(GetJobCmdResult, self).__init__(resp)
        # job cmd
        self.cmd = _bget(self.response.text, 'cmd', str)


class ActiveWorkflowResult(RequestResult):
    def __init__(self, resp):
        super(ActiveWorkflowResult, self).__init__(resp)
        # task 名称
        self.task_name = _bget(self.response.text, 'task_name', str)
        # task id
        self.task_id = _bget(self.response.text, 'task_id', str)


class DeleteTaskResult(RequestResult):
    def __init__(self, resp):
        super(DeleteTaskResult, self).__init__(resp)


class StopTaskResult(RequestResult):
    def __init__(self, resp):
        super(StopTaskResult, self).__init__(resp)


class ListWorkflowsResult(RequestResult):
    def __init__(self, resp):
        super(ListWorkflowsResult, self).__init__(resp)

        self.workflows = []

        self.count = 0


class GetWorkflowResult(RequestResult):
    def __init__(self, resp):
        super(GetWorkflowResult, self).__init__(resp)


class GetExcWorkflowResult(RequestResult):
    def __init__(self, resp):
        super(GetExcWorkflowResult, self).__init__(resp)

        self.parameter = _bget(self.response.text, 'parameter')


class DeleteWorkflowResult(RequestResult):
    def __init__(self, resp):
        super(DeleteWorkflowResult, self).__init__(resp)


class CreateWorkflowResult(RequestResult):
    def __init__(self, resp):
        super(CreateWorkflowResult, self).__init__(resp)


class PutWorkflowResult(RequestResult):
    def __init__(self, resp):
        super(PutWorkflowResult, self).__init__(resp)


class SetWorkflowParamResult(RequestResult):
    def __init__(self, resp):
        super(SetWorkflowParamResult, self).__init__(resp)


class GetToolResult(RequestResult):
    def __init__(self, resp):
        super(GetToolResult, self).__init__(resp)


class ListToolResult(RequestResult):
    def __init__(self, resp):
        super(ListToolResult, self).__init__(resp)

        self.tools = []

        self.count = 0


class GetToolParamResult(RequestResult):
    def __init__(self, resp):
        super(GetToolParamResult, self).__init__(resp)

        self.parameters = []


class DeleteToolResult(RequestResult):
    def __init__(self, resp):
        super(DeleteToolResult, self).__init__(resp)


class CreateToolResult(RequestResult):
    def __init__(self, resp):
        super(CreateToolResult, self).__init__(resp)


class PutToolResult(RequestResult):
    def __init__(self, resp):
        super(PutToolResult, self).__init__(resp)
