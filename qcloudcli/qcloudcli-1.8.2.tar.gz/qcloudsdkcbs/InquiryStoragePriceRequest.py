#!/usr/bin/python
# -*- coding: utf-8 -*-
from qcloudsdkcore.request import Request
class InquiryStoragePriceRequest(Request):

	def __init__(self):
		Request.__init__(self, 'cbs', 'qcloudcliV1', 'InquiryStoragePrice', 'cbs.api.qcloud.com')

	def get_inquiryType(self):
		return self.get_params().get('inquiryType')

	def set_inquiryType(self, inquiryType):
		self.add_param('inquiryType', inquiryType)

	def get_storageSize(self):
		return self.get_params().get('storageSize')

	def set_storageSize(self, storageSize):
		self.add_param('storageSize', storageSize)

	def get_storageType(self):
		return self.get_params().get('storageType')

	def set_storageType(self, storageType):
		self.add_param('storageType', storageType)

	def get_payMode(self):
		return self.get_params().get('payMode')

	def set_payMode(self, payMode):
		self.add_param('payMode', payMode)

	def get_period(self):
		return self.get_params().get('period')

	def set_period(self, period):
		self.add_param('period', period)

	def get_goodsNum(self):
		return self.get_params().get('goodsNum')

	def set_goodsNum(self, goodsNum):
		self.add_param('goodsNum', goodsNum)

	def get_storageId(self):
		return self.get_params().get('storageId')

	def set_storageId(self, storageId):
		self.add_param('storageId', storageId)

