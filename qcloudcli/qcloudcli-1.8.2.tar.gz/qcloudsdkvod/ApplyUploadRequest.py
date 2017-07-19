#!/usr/bin/python
# -*- coding: utf-8 -*-
from qcloudsdkcore.request import Request
class ApplyUploadRequest(Request):

	def __init__(self):
		Request.__init__(self, 'vod', 'qcloudcliV1', 'ApplyUpload', 'vod.api.qcloud.com')

	def get_videoType(self):
		return self.get_params().get('videoType')

	def set_videoType(self, videoType):
		self.add_param('videoType', videoType)

	def get_videoName(self):
		return self.get_params().get('videoName')

	def set_videoName(self, videoName):
		self.add_param('videoName', videoName)

	def get_videoSize(self):
		return self.get_params().get('videoSize')

	def set_videoSize(self, videoSize):
		self.add_param('videoSize', videoSize)

	def get_coverName(self):
		return self.get_params().get('coverName')

	def set_coverName(self, coverName):
		self.add_param('coverName', coverName)

	def get_coverType(self):
		return self.get_params().get('coverType')

	def set_coverType(self, coverType):
		self.add_param('coverType', coverType)

	def get_coverSize(self):
		return self.get_params().get('coverSize')

	def set_coverSize(self, coverSize):
		self.add_param('coverSize', coverSize)

	def get_procedure(self):
		return self.get_params().get('procedure')

	def set_procedure(self, procedure):
		self.add_param('procedure', procedure)

	def get_expireTime(self):
		return self.get_params().get('expireTime')

	def set_expireTime(self, expireTime):
		self.add_param('expireTime', expireTime)

	def get_storageRegion(self):
		return self.get_params().get('storageRegion')

	def set_storageRegion(self, storageRegion):
		self.add_param('storageRegion', storageRegion)

