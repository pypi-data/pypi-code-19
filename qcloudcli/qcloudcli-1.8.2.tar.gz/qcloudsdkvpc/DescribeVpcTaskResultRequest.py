#!/usr/bin/python
# -*- coding: utf-8 -*-
from qcloudsdkcore.request import Request
class DescribeVpcTaskResultRequest(Request):

	def __init__(self):
		Request.__init__(self, 'vpc', 'qcloudcliV1', 'DescribeVpcTaskResult', 'vpc.api.qcloud.com')

	def get_taskId(self):
		return self.get_params().get('taskId')

	def set_taskId(self, taskId):
		self.add_param('taskId', taskId)

