#!/usr/bin/python
# -*- coding: utf-8 -*-
from qcloudsdkcore.request import Request
class ModifyCbsStorageAttributesRequest(Request):

	def __init__(self):
		Request.__init__(self, 'cbs', 'qcloudcliV1', 'ModifyCbsStorageAttributes', 'cbs.api.qcloud.com')

	def get_storageId(self):
		return self.get_params().get('storageId')

	def set_storageId(self, storageId):
		self.add_param('storageId', storageId)

	def get_storageName(self):
		return self.get_params().get('storageName')

	def set_storageName(self, storageName):
		self.add_param('storageName', storageName)

	def get_projectId(self):
		return self.get_params().get('projectId')

	def set_projectId(self, projectId):
		self.add_param('projectId', projectId)

