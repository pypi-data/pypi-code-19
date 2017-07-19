#!/usr/bin/python
# -*- coding: utf-8 -*-
from qcloudsdkcore.request import Request
class DescribeDBInstancesV3Request(Request):

	def __init__(self):
		Request.__init__(self, 'cdb', 'qcloudcliV1', 'DescribeDBInstancesV3', 'cdb.api.qcloud.com')

	def get_projectIds(self):
		return self.get_params().get('projectIds')

	def set_projectIds(self, projectIds):
		self.add_param('projectIds', projectIds)

	def get_instanceIds(self):
		return self.get_params().get('instanceIds')

	def set_instanceIds(self, instanceIds):
		self.add_param('instanceIds', instanceIds)

	def get_instanceTypes(self):
		return self.get_params().get('instanceTypes')

	def set_instanceTypes(self, instanceTypes):
		self.add_param('instanceTypes', instanceTypes)

	def get_vips(self):
		return self.get_params().get('vips')

	def set_vips(self, vips):
		self.add_param('vips', vips)

	def get_status(self):
		return self.get_params().get('status')

	def set_status(self, status):
		self.add_param('status', status)

	def get_offset(self):
		return self.get_params().get('offset')

	def set_offset(self, offset):
		self.add_param('offset', offset)

	def get_limit(self):
		return self.get_params().get('limit')

	def set_limit(self, limit):
		self.add_param('limit', limit)

