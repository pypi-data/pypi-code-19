# -*- coding:utf-8 -*-

import json
from . import defaults
from . import http
from . import yml_utils
from . import exceptions
from . import utils
from .compat import urlparse, to_unicode, to_string, to_json
from .models import *
import time


def _normalize_endpoint(endpoint):
    if not endpoint.startswith('http://') and not endpoint.startswith('https://'):
        return 'https://' + endpoint
    else:
        return endpoint


class _Base(object):
    def __init__(self, auth, endpoint, operation, connect_timeout):
        self.session = http.Session()
        self.auth = auth
        self.endpoint = _normalize_endpoint(endpoint)
        self.operation = operation
        self.timeout = defaults.get(connect_timeout, defaults.connect_timeout)
        self._make_url = _UrlMaker(self.endpoint, self.operation)

    def _do(self, method, res_account_name, project_name, target, **kwargs):
        target = to_string(target)
        self.data = kwargs.pop('data', None)
        self.params = kwargs.pop('params', None)
        req = http.Request(method, self.auth, self._make_url(res_account_name, project_name, target, **kwargs), data=self.data, params=self.params)

        resp = self.session.do_request(req, timeout=self.timeout)
        if resp.status // 100 != 2:
            raise exceptions.make_exception(resp)

        return resp

    def _parse_result(self, resp, parse_func, klass):
        result = klass(resp)
        parse_func(result, resp.response.content)
        return result

    def _get_url(self, res_account_name, res_project_name, target, **kwargs):
        return self._make_url(res_account_name, res_project_name, target, **kwargs)


class _UrlMaker(object):

    def __init__(self, endpoint, operation):
        p = urlparse(endpoint)

        self.scheme = p.scheme
        self.netloc = p.netloc
        self.operation = operation

    def __call__(self, res_account_name, res_project_name, target, **kwargs):
        self.project_name = res_project_name
        self.account_name = res_account_name
        if target:
            if not len(kwargs):
                return '{0}://{1}/accounts/{2}/projects/{3}/{4}/{5}/'.format(self.scheme, self.netloc, self.account_name, self.project_name, self.operation, target)
            else:
                params = list()
                for item in kwargs:
                    if kwargs.get(item):
                        params.append(item + '=' + str(kwargs.get(item)))
                parameters = '?' + '&'.join(params)
                return '{0}://{1}/accounts/{2}/projects/{3}/{4}/{5}/{6}'.format(self.scheme, self.netloc, self.account_name, self.project_name, self.operation, target, parameters)
        else:
            return '{0}://{1}/accounts/{2}/projects/{3}/{4}/'.format(self.scheme, self.netloc, self.account_name, self.project_name, self.operation)


class Tasks(_Base):
    """ 用于Tasks操作的类
    :param auth: 包含了用户认证信息的Auth对象
    :type auth: gdpy.GeneDockAuth

    :param str endpoint: 访问域名，如北京区域的域名为cn-beijing-api.genedock.com
    :param str res_account_name: 指定从该账号下获取资源(如需获取公共资源，则为public)
    :param str res_project_name: 指定从该项目下获取资源(默认为default)
    :raises: 如果获取或上传失败，则抛出来自服务端的异常; 还可能抛出其他异常
    tasks related operations
    usage::
        >>> import gdpy
        >>> auth = gdpy.GeneDockAuth('access_key_id', 'access_key_secret')
        >>> task = gdpy.Tasks(auth, 'https://cn-beijing-api.genedock.com', 'res_account_name', 'project_name')
    """
    def __init__(self, auth, endpoint, res_account_name, project_name='default', connect_timeout=None):
        self.operation = 'tasks'
        super(Tasks, self).__init__(auth, endpoint, self.operation, connect_timeout)
        self.res_account_name = res_account_name
        self.res_project_name = project_name

    def __do_task(self, method, id=None, **kwargs):
        return self._do(method, self.res_account_name, self.res_project_name, id, **kwargs)

    def get_task(self, id):
        """
        usage:
            >>> resp = task.get_task('task_id')
        """
        super(Tasks, self).__init__(self.auth, self.endpoint, 'tasks', self.timeout)
        resp = self.__do_task('GET', id)
        return GetTaskResult(resp)

    def list_tasks(self, **kwargs):
        """
        usage:
            >>> resp = task.list_tasks()
        """
        super(Tasks, self).__init__(self.auth, self.endpoint, 'tasks', self.timeout)
        default_to = int(time.time())
        default_from = default_to - 60 * 60 * 24 * 7
        params = {'from': default_from, 'to': default_to}
        if 'params' in list(kwargs.keys()):
            resp = self.__do_task('GET', **kwargs)
        else:
            resp = self.__do_task('GET', params=params, **kwargs)
        return self._parse_result(resp, yml_utils.parse_list_tasks, ListTasksResult)

    def active_workflow(self, param_file, workflow_name, workflow_version, workflow_owner=None):
        """
        usage::
            >>> resp = task.active_workflow('workflow_param_file', 'workflow_name', 'workflow_version')
        """
        if not workflow_owner:
            workflow_owner = self.res_account_name
        if not is_object_name_valid(workflow_name):
            raise ValueError("Invalid workflow name! Expect a string started with alphabet and under 128 characters, but got {}!".format(str(workflow_name)))
        if not is_object_version_valid(workflow_version):
            raise ValueError("Invalid workflow version! Expect interger greater than 0, but got {}".format(str(workflow_version)))
        try:
            data = dict()
            data["parameters"] = yml_utils.yaml_loader(param_file)
            data["workflow_name"] = workflow_name
            data["workflow_version"] = int(workflow_version)
            data["workflow_owner"] = workflow_owner
            data["task_name"] = data["parameters"].get("name")
            super(Tasks, self).__init__(self.auth, self.endpoint, 'tasks', self.timeout)
            resp = self.__do_task('POST', '', data=data)
        except ValueError as e:
            raise e
        return ActiveWorkflowResult(resp)

    def delete_task(self, id):
        """
        usage:
            >>> resp = task.delete_task('task_id')
        """
        super(Tasks, self).__init__(self.auth, self.endpoint, 'tasks', self.timeout)
        resp = self.__do_task('DELETE', id)
        return DeleteTaskResult(resp)

    def stop_task(self, id):
        """
        usage:
            >>> resp = task.stop_task('task_id')
        """
        super(Tasks, self).__init__(self.auth, self.endpoint, 'tasks', self.timeout)
        resp = self.__do_task('PUT', id)
        return StopTaskResult(resp)

    def get_jobs(self, id):
        """
        usage:
            >>> resp = task.get_jobs('task_id')
        """
        target = id + '/jobs'
        super(Tasks, self).__init__(self.auth, self.endpoint, 'tasks', self.timeout)
        resp = self.__do_task('GET', target)
        return self._parse_result(resp, yml_utils.parse_get_jobs, GetJobResult)

    def get_job_cmd(self, id):
        """
        usage:
            >>> resp = task.get_job_cmd('job_id')
        """
        task_id = id.split('_')[0]
        target = task_id + '/cmd/' + id
        super(Tasks, self).__init__(self.auth, self.endpoint, 'tasks', self.timeout)
        resp = self.__do_task('GET', target)
        return GetJobCmdResult(resp)


class Workflows(_Base):
    """ 用于Workflows操作的类
    :param auth: 包含了用户认证信息的Auth对象
    :type auth: gdpy.GeneDockAuth

    :param str endpoint: 访问域名，如北京区域的域名为cn-beijing-api.genedock.com
    :param str res_account_name: 指定从该账号下获取资源(如需获取公共资源，则为public)
    :param str res_project_name: 指定从该项目下获取资源(默认为default)
    :raises: 如果获取或上传失败，则抛出来自服务端的异常; 还可能抛出其他异常
    workflows related operations
    usage::
        >>> import gdpy
        >>> auth = gdpy.GeneDockAuth('access_key_id', 'access_key_secret')
        >>> workflow = gdpy.Workflows(auth, 'https://cn-beijing-api.genedock.com', 'res_account_name', 'project_name')
    """
    def __init__(self, auth, endpoint, res_account_name, project_name='default', operation='workflows', connect_timeout=None):
        self.operation = operation
        super(Workflows, self).__init__(auth, endpoint, self.operation, connect_timeout)
        self.res_account_name = res_account_name
        self.res_project_name = project_name

    def __do_workflow(self, method, name=None, version=None, **kwargs):
        if name is not None and not is_object_name_valid(name):
            raise ValueError("Invalid workflow name! Expect a string started with alphabet and under 128 characters, but got {}!".format(str(name)))
        if version is not None and not is_object_version_valid(version):
            raise ValueError("Invalid workflow version! Expect interger greater than 0, but got {}".format(str(version)))
        return self._do(method, self.res_account_name, self.res_project_name, name, workflow_version=version, **kwargs)

    def list_workflows(self):
        """
        usage:
            >>> resp = workflow.list_workflows()
        """
        resp = self.__do_workflow('GET')
        super(Workflows, self).__init__(self.auth, self.endpoint, 'workflows', self.timeout)
        return self._parse_result(resp, yml_utils.parse_list_workflows, ListWorkflowsResult)

    def list_exc_workflows(self):
        """
        usage:
            >>> resp = workflow.list_exc_workflows()
        """
        super(Workflows, self).__init__(self.auth, self.endpoint, 'executable-workflows', self.timeout)
        resp = self.__do_workflow('GET')
        return self._parse_result(resp, yml_utils.parse_list_workflows, ListWorkflowsResult)

    def get_workflow(self, name, version=None):
        """
        usage:
            >>> resp = workflow.get_workflow('workflow_name', 'workflow_version')
            */Or lack version/*
            >>> resp = workflow.get_workflow('workflow_name')
        """
        if name is None:
            raise ValueError("Expect a name(str) started with alphabet and under 128 characters")
        super(Workflows, self).__init__(self.auth, self.endpoint, 'workflows', self.timeout)
        resp = self.__do_workflow('GET', name, version)
        return GetWorkflowResult(resp)

    def get_exc_workflow(self, name, version):
        """
        usage:
            >>> resp = workflow.get_exc_workflow('workflow_name', 'workflow_version')
        """
        if name is None:
            raise ValueError("Expect a name(str) started with alphabet and under 128 characters")
        if version is None:
            raise ValueError("Expect interger greater than 0 as version")
        super(Workflows, self).__init__(self.auth, self.endpoint, 'executable-workflows', self.timeout)
        resp = self.__do_workflow('GET', name, version)
        return GetExcWorkflowResult(resp)

        """
        get a yaml tempalte:
            >>> from gdpy.yml_utils import yaml_dumper
            >>> yml_template = yaml_dumper(resp.parameter)
        """

    def delete_workflow(self, name, version):
        """
        usage:
            >>> resp = workflow.delete_workflow('workflow_name', 'workflow_version')
        """
        if name is None:
            raise ValueError("Expect a name(str) started with alphabet and under 128 characters")
        if version is None:
            raise ValueError("Expect interger greater than 0 as version")
        super(Workflows, self).__init__(self.auth, self.endpoint, 'workflows', self.timeout)
        resp = self.__do_workflow('DELETE', name, version)
        return DeleteWorkflowResult(resp)

    def create_workflow(self, name, version, description=''):
        """
        usage:
            >>> resp = workflow.create_workflow('workflow_name', 'workflow_version', 'description')
        """
        if not is_object_name_valid(name):
            raise ValueError("Invalid workflow name! Expect a string started with alphabet and under 128 characters, but got {}!".format(str(name)))
        if not is_object_version_valid(version):
            raise ValueError("Invalid workflow version! Expect interger greater than 0, but got {}".format(str(version)))
        data = {"workflow_name": name, "workflow_version": version, "description": description}
        super(Workflows, self).__init__(self.auth, self.endpoint, 'workflows', self.timeout)
        resp = self.__do_workflow('POST', data=data)
        return CreateWorkflowResult(resp)

    def put_workflow(self, param_file):
        """
        usage:
            >>> resp = workflow.put_workflow('parameter_file_path')
        """
        workflow_temp = yml_utils.yaml_loader(param_file)
        workflow_description = workflow_temp.get('workflow').get('description', '')
        if not is_object_name_valid(workflow_temp.get('workflow').get('name')):
            raise ValueError("Invalid workflow name! Expect a string started with alphabet and under 128 characters, but got {}!".format(str(workflow_temp.get('workflow').get('name'))))
        else:
            workflow_name = str(workflow_temp.get('workflow').get('name'))
        if not is_object_version_valid(workflow_temp.get('workflow').get('version')):
            raise ValueError("Invalid tool version! Expect interger greater than 0, but got {}".format(str(workflow_temp.get('workflow').get('version'))))
        else:
            workflow_version = int(workflow_temp.get('workflow').get('version'))
        workflow_configs = {'nodelist': workflow_temp.get('workflow').get('nodelist')}
        try:
            data = dict()
            data["workflow_version"] = workflow_version
            data["configs"] = workflow_configs
            data["description"] = workflow_description
            super(Workflows, self).__init__(self.auth, self.endpoint, 'workflows', self.timeout)
            resp = self.__do_workflow('PUT', workflow_name, data=data)
        except ValueError as e:
            raise e
        return PutWorkflowResult(resp)

    def set_workflow_param(self, param_file, name, version):
        """
        usage:
            >>> resp = workflow.set_workflow_param('exec_workflow_param_file', 'workflow_name', 'workflow_version')
        """
        if not is_object_name_valid(name):
            raise ValueError("Invalid workflow name! Expect a string started with alphabet and under 128 characters, but got {}!".format(str(name)))
        if not is_object_version_valid(version):
            raise ValueError("Invalid workflow version! Expect interger greater than 0, but got {}".format(str(version)))
        workflow_temp = yml_utils.yaml_loader(param_file)
        data = {'workflow_version': version, 'parameters': workflow_temp}
        super(Workflows, self).__init__(self.auth, self.endpoint, 'executable-workflows', self.timeout)
        resp = self.__do_workflow('PUT', name, data=data)
        return SetWorkflowParamResult(resp)


class Tools(_Base):
    """ 用于Tools操作的类
    :param auth: 包含了用户认证信息的Auth对象
    :type auth: gdpy.GeneDockAuth

    :param str endpoint: 访问域名，如北京区域的域名为cn-beijing-api.genedock.com
    :param str res_account_name: 指定从该账号下获取资源(如需获取公共资源，则为public)
    :param str res_project_name: 指定从该项目下获取资源(默认为default)
    :raises: 如果获取或上传失败，则抛出来自服务端的异常; 还可能抛出其他异常
    tools related operations
    usage::
        >>> import gdpy
        >>> auth = gdpy.GeneDockAuth('access_key_id', 'access_key_secret')
        >>> tool = gdpy.Tools(auth, 'https://cn-beijing-api.genedock.com', 'res_account_name', 'project_name')
    """
    def __init__(self, auth, endpoint, res_account_name, project_name='default', operation='tools', connect_timeout=None):
        self.operation = operation
        super(Tools, self).__init__(auth, endpoint, self.operation, connect_timeout)
        self.res_account_name = res_account_name
        self.res_project_name = project_name

    def __do_tool(self, method, name=None, version=None, **kwargs):
        if name is not None and not is_object_name_valid(name):
            raise ValueError("Invalid tool name! Expect a string started with alphabet and under 128 characters, but got {}!".format(str(name)))
        if version is not None and not is_object_version_valid(version):
            raise ValueError("Invalid tool version! Expect interger greater than 0, but got {}".format(str(version)))
        return self._do(method, self.res_account_name, self.res_project_name, name, tool_version=version, **kwargs)

    def get_tool(self, name, version=None):
        """
        usage:
            >>> resp = tool.get_tool('tool_name', 'tool_version')
            */Or lack version/*
            >>> resp = tool.get_tool('tool_name')
        """
        if name is None:
            raise ValueError("Expect a name(str) started with alphabet and under 128 characters")
        super(Tools, self).__init__(self.auth, self.endpoint, 'tools', self.timeout)
        resp = self.__do_tool('GET', name, version)
        return GetToolResult(resp)

    def list_tools(self):
        """
        usage:
            >>> resp = tool.list_tools()
        """
        super(Tools, self).__init__(self.auth, self.endpoint, 'tools', self.timeout)
        resp = self.__do_tool('GET')
        return self._parse_result(resp, yml_utils.parse_list_tools, ListToolResult)

    def get_tool_param(self, name, version=None):
        """
        usage:
            >>> resp = tool.get_tool_param('tool_name', 'tool_version')
            */Or lack version/*
            >>> resp = tool.get_tool_param('tool_name')
        """
        if name is None:
            raise ValueError("Expect a name(str) started with alphabet and under 128 characters")
        super(Tools, self).__init__(self.auth, self.endpoint, 'toolparameters', self.timeout)
        resp = self.__do_tool('GET', name, version)
        return self._parse_result(resp, yml_utils.parse_get_tool_parameters, GetToolParamResult)

    def delete_tool(self, name, version):
        """
        usage:
            >>> resp = tool.delete_tool('tool_name', 'tool_version')
        """
        if name is None:
            raise ValueError("Expect a name(str) started with alphabet and under 128 characters")
        if version is None:
            raise ValueError("Expect interger greater than 0 as version")
        super(Tools, self).__init__(self.auth, self.endpoint, 'tools', self.timeout)
        resp = self.__do_tool('DELETE', name, version)
        return DeleteToolResult(resp)

    def create_tool(self, name, version, description=''):
        """
        usage:
            >>> resp = tool.create_tool('tool_name', 'tool_version', 'description')
        """
        if not is_object_name_valid(name):
            raise ValueError("Invalid tool name! Expect a string started with alphabet and under 128 characters, but got {}!".format(str(name)))
        if not is_object_version_valid(version):
            raise ValueError("Invalid tool version! Expect interger greater than 0, but got {}".format(str(version)))
        data = {"tool_name": name, "tool_version": version, "description": description}
        super(Tools, self).__init__(self.auth, self.endpoint, 'tools', self.timeout)
        resp = self.__do_tool('POST', data=data)
        return CreateToolResult(resp)

    def put_tool(self, param_file):
        """
        usage:
            >>> resp = tool.put_tool('parameter_file_path')
        """
        tool_temp = yml_utils.yaml_loader(param_file)
        tool_description = tool_temp.get('app').get('description', '')
        if not is_object_name_valid(tool_temp.get('app').get('name')):
            raise ValueError("Invalid tool name! Expect a string started with alphabet and under 128 characters, but got {}!".format(str(name)))
        else:
            tool_name = str(tool_temp.get('app').get('name'))
        if not is_object_version_valid(tool_temp.get('app').get('version')):
            raise ValueError("Invalid tool version! Expect interger greater than 0, but got {}".format(str(version)))
        else:
            tool_version = int(tool_temp.get('app').get('version'))
        tool_configs = tool_temp.get('app')
        try:
            data = dict()
            data["tool_version"] = tool_version
            data["configs"] = tool_configs
            data["description"] = tool_description
            super(Tools, self).__init__(self.auth, self.endpoint, 'tools', self.timeout)
            resp = self.__do_tool('PUT', tool_name, data=data)
        except ValueError as e:
            raise e
        return PutToolResult(resp)
