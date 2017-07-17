#
#  BEGIN LICENSE
#  Copyright (c) Blue Mind SAS, 2012-2016
# 
#  This file is part of BlueMind. BlueMind is a messaging and collaborative
#  solution.
# 
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of either the GNU Affero General Public License as
#  published by the Free Software Foundation (version 3 of the License).
# 
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
#  See LICENSE.txt
#  END LICENSE
#
import requests
import json
from netbluemind.python import serder
from netbluemind.python.client import BaseEndpoint

class IDataProtect(BaseEndpoint):
	def __init__(self, apiKey, url ):
		self.url = url
		self.apiKey = apiKey
		self.base = url +'/dataprotect'

	def saveAll (self):
		postUri = "/_backup";
		data = None
		queryParams = {  };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.task.api.TaskRef import TaskRef
		from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
		return self.handleResult__(__TaskRefSerDer__(), response)
	def getContent (self, partGen ):
		postUri = "/_content/{partGen}";
		data = None
		postUri = postUri.replace("{partGen}",partGen);
		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.task.api.TaskRef import TaskRef
		from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
		return self.handleResult__(__TaskRefSerDer__(), response)
	def run (self, restoreDefinition ):
		postUri = "/restore";
		data = None
		from netbluemind.dataprotect.api.RestoreDefinition import RestoreDefinition
		from netbluemind.dataprotect.api.RestoreDefinition import __RestoreDefinitionSerDer__
		data = __RestoreDefinitionSerDer__().encode(restoreDefinition)

		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.task.api.TaskRef import TaskRef
		from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
		return self.handleResult__(__TaskRefSerDer__(), response)
	def getRestoreCapabilitiesByTags (self, tags ):
		postUri = "/restore/_capabilities_by_tags";
		data = None
		data = serder.ListSerDer(serder.STRING).encode(tags)

		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.dataprotect.api.RestoreOperation import RestoreOperation
		from netbluemind.dataprotect.api.RestoreOperation import __RestoreOperationSerDer__
		return self.handleResult__(serder.ListSerDer(__RestoreOperationSerDer__()), response)
	def installFromGeneration (self, generationId ):
		postUri = "/_install";
		data = None
		queryParams = {  'generationId': generationId   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.task.api.TaskRef import TaskRef
		from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
		return self.handleResult__(__TaskRefSerDer__(), response)
	def forget (self, generationId ):
		postUri = "/generations";
		data = None
		queryParams = {  'generationId': generationId   };

		response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.task.api.TaskRef import TaskRef
		from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
		return self.handleResult__(__TaskRefSerDer__(), response)
	def getRestoreCapabilities (self):
		postUri = "/restore/_capabilities";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.dataprotect.api.RestoreOperation import RestoreOperation
		from netbluemind.dataprotect.api.RestoreOperation import __RestoreOperationSerDer__
		return self.handleResult__(serder.ListSerDer(__RestoreOperationSerDer__()), response)
	def getRetentionPolicy (self):
		postUri = "/policy";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.dataprotect.api.RetentionPolicy import RetentionPolicy
		from netbluemind.dataprotect.api.RetentionPolicy import __RetentionPolicySerDer__
		return self.handleResult__(__RetentionPolicySerDer__(), response)
	def updatePolicy (self, rp ):
		postUri = "/policy";
		data = None
		from netbluemind.dataprotect.api.RetentionPolicy import RetentionPolicy
		from netbluemind.dataprotect.api.RetentionPolicy import __RetentionPolicySerDer__
		data = __RetentionPolicySerDer__().encode(rp)

		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getAvailableGenerations (self):
		postUri = "/generations";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.dataprotect.api.DataProtectGeneration import DataProtectGeneration
		from netbluemind.dataprotect.api.DataProtectGeneration import __DataProtectGenerationSerDer__
		return self.handleResult__(serder.ListSerDer(__DataProtectGenerationSerDer__()), response)
	def syncWithFilesystem (self):
		postUri = "/_syncfs";
		data = None
		queryParams = {  };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
