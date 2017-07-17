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

class IMailshare(BaseEndpoint):
	def __init__(self, apiKey, url ,domainUid ):
		self.url = url
		self.apiKey = apiKey
		self.base = url +'/mailshares/{domainUid}'
		self.domainUid_ = domainUid
		self.base = self.base.replace('{domainUid}',domainUid)

	def update (self, uid , mailshare ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.mailshare.api.Mailshare import Mailshare
		from netbluemind.mailshare.api.Mailshare import __MailshareSerDer__
		data = __MailshareSerDer__().encode(mailshare)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def delete (self, uid ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getComplete (self, uid ):
		postUri = "/{uid}/complete";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.mailshare.api.Mailshare import Mailshare
		from netbluemind.mailshare.api.Mailshare import __MailshareSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(__ItemValueSerDer__(__MailshareSerDer__()), response)
	def create (self, uid , mailshare ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.mailshare.api.Mailshare import Mailshare
		from netbluemind.mailshare.api.Mailshare import __MailshareSerDer__
		data = __MailshareSerDer__().encode(mailshare)

		queryParams = {    };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def allComplete (self):
		postUri = "/_complete";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.mailshare.api.Mailshare import Mailshare
		from netbluemind.mailshare.api.Mailshare import __MailshareSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__MailshareSerDer__())), response)
