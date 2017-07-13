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
class OpsDescribeDisksRequest(RpcRequest):

	def __init__(self):
		RpcRequest.__init__(self, 'Ecs', '2014-05-26', 'OpsDescribeDisks','ecs')

	def get_EcsInstanceId(self):
		return self.get_query_params().get('EcsInstanceId')

	def set_EcsInstanceId(self,EcsInstanceId):
		self.add_query_param('EcsInstanceId',EcsInstanceId)

	def get_FuzzyDiskName(self):
		return self.get_query_params().get('FuzzyDiskName')

	def set_FuzzyDiskName(self,FuzzyDiskName):
		self.add_query_param('FuzzyDiskName',FuzzyDiskName)

	def get_IzNo(self):
		return self.get_query_params().get('IzNo')

	def set_IzNo(self,IzNo):
		self.add_query_param('IzNo',IzNo)

	def get_SnapshotId(self):
		return self.get_query_params().get('SnapshotId')

	def set_SnapshotId(self,SnapshotId):
		self.add_query_param('SnapshotId',SnapshotId)

	def get_ImageId(self):
		return self.get_query_params().get('ImageId')

	def set_ImageId(self,ImageId):
		self.add_query_param('ImageId',ImageId)

	def get_EnableAutoSnapshot(self):
		return self.get_query_params().get('EnableAutoSnapshot')

	def set_EnableAutoSnapshot(self,EnableAutoSnapshot):
		self.add_query_param('EnableAutoSnapshot',EnableAutoSnapshot)

	def get_Active(self):
		return self.get_query_params().get('Active')

	def set_Active(self,Active):
		self.add_query_param('Active',Active)

	def get_CreateTimeFrom(self):
		return self.get_query_params().get('CreateTimeFrom')

	def set_CreateTimeFrom(self,CreateTimeFrom):
		self.add_query_param('CreateTimeFrom',CreateTimeFrom)

	def get_Portable(self):
		return self.get_query_params().get('Portable')

	def set_Portable(self,Portable):
		self.add_query_param('Portable',Portable)

	def get_DiskType(self):
		return self.get_query_params().get('DiskType')

	def set_DiskType(self,DiskType):
		self.add_query_param('DiskType',DiskType)

	def get_RegionNo(self):
		return self.get_query_params().get('RegionNo')

	def set_RegionNo(self,RegionNo):
		self.add_query_param('RegionNo',RegionNo)

	def get_ExcludeStatus(self):
		return self.get_query_params().get('ExcludeStatus')

	def set_ExcludeStatus(self,ExcludeStatus):
		self.add_query_param('ExcludeStatus',ExcludeStatus)

	def get_DeleteAutoSnapshot(self):
		return self.get_query_params().get('DeleteAutoSnapshot')

	def set_DeleteAutoSnapshot(self,DeleteAutoSnapshot):
		self.add_query_param('DeleteAutoSnapshot',DeleteAutoSnapshot)

	def get_DiskCategory(self):
		return self.get_query_params().get('DiskCategory')

	def set_DiskCategory(self,DiskCategory):
		self.add_query_param('DiskCategory',DiskCategory)

	def get_CreateTimeTo(self):
		return self.get_query_params().get('CreateTimeTo')

	def set_CreateTimeTo(self,CreateTimeTo):
		self.add_query_param('CreateTimeTo',CreateTimeTo)

	def get_DiskIds(self):
		return self.get_query_params().get('DiskIds')

	def set_DiskIds(self,DiskIds):
		self.add_query_param('DiskIds',DiskIds)

	def get_DeleteWithInstance(self):
		return self.get_query_params().get('DeleteWithInstance')

	def set_DeleteWithInstance(self,DeleteWithInstance):
		self.add_query_param('DeleteWithInstance',DeleteWithInstance)

	def get_Status(self):
		return self.get_query_params().get('Status')

	def set_Status(self,Status):
		self.add_query_param('Status',Status)