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

class IJob(BaseEndpoint):
	def __init__(self, apiKey, url ):
		self.url = url
		self.apiKey = apiKey
		self.base = url +'/scheduledjobs'

	def deleteExecutions (self, executions ):
		postUri = "/_deleteExecutions";
		data = None
		data = serder.ListSerDer(serder.INT).encode(executions)

		queryParams = {   };

		response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getLogs (self, jobExecution , offset ):
		postUri = "/_logs";
		data = None
		from netbluemind.scheduledjob.api.JobExecution import JobExecution
		from netbluemind.scheduledjob.api.JobExecution import __JobExecutionSerDer__
		data = __JobExecutionSerDer__().encode(jobExecution)

		queryParams = {   'offset': offset   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.scheduledjob.api.LogEntry import LogEntry
		from netbluemind.scheduledjob.api.LogEntry import __LogEntrySerDer__
		return self.handleResult__(serder.SetSerDer(__LogEntrySerDer__()), response)
	def start (self, jobId , domainName ):
		postUri = "/_start/{jobId}";
		data = None
		postUri = postUri.replace("{jobId}",jobId);
		queryParams = {   'domainName': domainName   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def searchJob (self, query ):
		postUri = "/_searchJob";
		data = None
		from netbluemind.scheduledjob.api.JobQuery import JobQuery
		from netbluemind.scheduledjob.api.JobQuery import __JobQuerySerDer__
		data = __JobQuerySerDer__().encode(query)

		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.scheduledjob.api.Job import Job
		from netbluemind.scheduledjob.api.Job import __JobSerDer__
		from netbluemind.core.api.ListResult import ListResult
		from netbluemind.core.api.ListResult import __ListResultSerDer__
		return self.handleResult__(__ListResultSerDer__(__JobSerDer__()), response)
	def update (self, job ):
		postUri = "/_updateJob";
		data = None
		from netbluemind.scheduledjob.api.Job import Job
		from netbluemind.scheduledjob.api.Job import __JobSerDer__
		data = __JobSerDer__().encode(job)

		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def searchExecution (self, query ):
		postUri = "/_searchExecution";
		data = None
		from netbluemind.scheduledjob.api.JobExecutionQuery import JobExecutionQuery
		from netbluemind.scheduledjob.api.JobExecutionQuery import __JobExecutionQuerySerDer__
		data = __JobExecutionQuerySerDer__().encode(query)

		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.scheduledjob.api.JobExecution import JobExecution
		from netbluemind.scheduledjob.api.JobExecution import __JobExecutionSerDer__
		from netbluemind.core.api.ListResult import ListResult
		from netbluemind.core.api.ListResult import __ListResultSerDer__
		return self.handleResult__(__ListResultSerDer__(__JobExecutionSerDer__()), response)
	def deleteExecution (self, jobExecutionId ):
		postUri = "/_deleteExecution";
		data = None
		queryParams = {  'jobExecutionId': jobExecutionId   };

		response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getJobFromId (self, jobId ):
		postUri = "/_job/{jobId}";
		data = None
		postUri = postUri.replace("{jobId}",jobId);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.scheduledjob.api.Job import Job
		from netbluemind.scheduledjob.api.Job import __JobSerDer__
		return self.handleResult__(__JobSerDer__(), response)
