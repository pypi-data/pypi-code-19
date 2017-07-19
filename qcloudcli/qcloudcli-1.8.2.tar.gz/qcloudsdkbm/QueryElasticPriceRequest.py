#!/usr/bin/python
# -*- coding: utf-8 -*-
from qcloudsdkcore.request import Request
class QueryElasticPriceRequest(Request):

	def __init__(self):
		Request.__init__(self, 'bm', 'qcloudcliV1', 'QueryElasticPrice', 'bm.api.qcloud.com')

	def get_cpuId(self):
		return self.get_params().get('cpuId')

	def set_cpuId(self, cpuId):
		self.add_param('cpuId', cpuId)

	def get_diskType(self):
		return self.get_params().get('diskType')

	def set_diskType(self, diskType):
		self.add_param('diskType', diskType)

	def get_diskSize(self):
		return self.get_params().get('diskSize')

	def set_diskSize(self, diskSize):
		self.add_param('diskSize', diskSize)

	def get_diskNum(self):
		return self.get_params().get('diskNum')

	def set_diskNum(self, diskNum):
		self.add_param('diskNum', diskNum)

	def get_haveRaidCard(self):
		return self.get_params().get('haveRaidCard')

	def set_haveRaidCard(self, haveRaidCard):
		self.add_param('haveRaidCard', haveRaidCard)

	def get_mem(self):
		return self.get_params().get('mem')

	def set_mem(self, mem):
		self.add_param('mem', mem)

	def get_timeSpan(self):
		return self.get_params().get('timeSpan')

	def set_timeSpan(self, timeSpan):
		self.add_param('timeSpan', timeSpan)

	def get_timeUnit(self):
		return self.get_params().get('timeUnit')

	def set_timeUnit(self, timeUnit):
		self.add_param('timeUnit', timeUnit)

	def get_goodsNum(self):
		return self.get_params().get('goodsNum')

	def set_goodsNum(self, goodsNum):
		self.add_param('goodsNum', goodsNum)

	def get_deviceClass(self):
		return self.get_params().get('deviceClass')

	def set_deviceClass(self, deviceClass):
		self.add_param('deviceClass', deviceClass)

