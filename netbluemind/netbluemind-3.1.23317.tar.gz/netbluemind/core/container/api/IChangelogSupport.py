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

class IChangelogSupport(BaseEndpoint):
	def __init__(self, apiKey, url ):
		self.url = url
		self.apiKey = apiKey
		self.base = url +''

	def getVersion (self):
		postUri = "/_version";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.LONG, response)
	def itemChangelog (self, uid , since ):
		postUri = "/{uid}/_itemchangelog";
		data = None
		postUri = postUri.replace("{uid}",uid);
		data = serder.LONG.encode(since)

		queryParams = {    };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.ItemChangelog import ItemChangelog
		from netbluemind.core.container.model.ItemChangelog import __ItemChangelogSerDer__
		return self.handleResult__(__ItemChangelogSerDer__(), response)
	def changeset (self, since ):
		postUri = "/_changeset";
		data = None
		queryParams = {  'since': since   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
		from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
		return self.handleResult__(__ContainerChangesetSerDer__(serder.STRING), response)
	def changesetById (self, since ):
		postUri = "/_changesetById";
		data = None
		queryParams = {  'since': since   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
		from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
		return self.handleResult__(__ContainerChangesetSerDer__(serder.LONG), response)
	def containerChangelog (self, since ):
		postUri = "/_changelog";
		data = None
		data = serder.LONG.encode(since)

		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.ContainerChangelog import ContainerChangelog
		from netbluemind.core.container.model.ContainerChangelog import __ContainerChangelogSerDer__
		return self.handleResult__(__ContainerChangelogSerDer__(), response)
