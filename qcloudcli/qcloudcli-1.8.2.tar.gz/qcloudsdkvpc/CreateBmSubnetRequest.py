#!/usr/bin/python
# -*- coding: utf-8 -*-
from qcloudsdkcore.request import Request
class CreateBmSubnetRequest(Request):

	def __init__(self):
		Request.__init__(self, 'vpc', 'qcloudcliV1', 'CreateBmSubnet', 'vpc.api.qcloud.com')

	def get_vpcId(self):
		return self.get_params().get('vpcId')

	def set_vpcId(self, vpcId):
		self.add_param('vpcId', vpcId)

	def get_subnetSet(self):
		return self.get_params().get('subnetSet')

	def set_subnetSet(self, subnetSet):
		self.add_param('subnetSet', subnetSet)

	def get_vlanId(self):
		return self.get_params().get('vlanId')

	def set_vlanId(self, vlanId):
		self.add_param('vlanId', vlanId)

	def get_dhcpEnable(self):
		return self.get_params().get('dhcpEnable')

	def set_dhcpEnable(self, dhcpEnable):
		self.add_param('dhcpEnable', dhcpEnable)

	def get_dhcpServerIp(self):
		return self.get_params().get('dhcpServerIp')

	def set_dhcpServerIp(self, dhcpServerIp):
		self.add_param('dhcpServerIp', dhcpServerIp)

	def get_ipReserve(self):
		return self.get_params().get('ipReserve')

	def set_ipReserve(self, ipReserve):
		self.add_param('ipReserve', ipReserve)

