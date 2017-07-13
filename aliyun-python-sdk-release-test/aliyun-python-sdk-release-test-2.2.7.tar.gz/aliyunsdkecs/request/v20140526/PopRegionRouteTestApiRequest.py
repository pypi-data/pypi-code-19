# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from aliyunsdkcore.request import RpcRequest
class PopRegionRouteTestApiRequest(RpcRequest):

	def __init__(self):
		RpcRequest.__init__(self, 'Ecs', '2014-05-26', 'PopRegionRouteTestApi','ecs')

	def get_Sleep(self):
		return self.get_query_params().get('Sleep')

	def set_Sleep(self,Sleep):
		self.add_query_param('Sleep',Sleep)

	def get_RequiredValue(self):
		return self.get_query_params().get('RequiredValue')

	def set_RequiredValue(self,RequiredValue):
		self.add_query_param('RequiredValue',RequiredValue)

	def get_RegionNo(self):
		return self.get_query_params().get('RegionNo')

	def set_RegionNo(self,RegionNo):
		self.add_query_param('RegionNo',RegionNo)