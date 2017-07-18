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

class IMailboxIdentity(BaseEndpoint):
	def __init__(self, apiKey, url ,domainUid ,mboxUid ):
		self.url = url
		self.apiKey = apiKey
		self.base = url +'/mailboxes/{domainUid}/identity/{mboxUid}'
		self.domainUid_ = domainUid
		self.base = self.base.replace('{domainUid}',domainUid)
		self.mboxUid_ = mboxUid
		self.base = self.base.replace('{mboxUid}',mboxUid)

	def update (self, uid , identity ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.mailbox.identity.api.Identity import Identity
		from netbluemind.mailbox.identity.api.Identity import __IdentitySerDer__
		data = __IdentitySerDer__().encode(identity)

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
	def get (self, uid ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.mailbox.identity.api.Identity import Identity
		from netbluemind.mailbox.identity.api.Identity import __IdentitySerDer__
		return self.handleResult__(__IdentitySerDer__(), response)
	def getPossibleIdentities (self):
		postUri = "/_possible";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.mailbox.identity.api.IdentityDescription import IdentityDescription
		from netbluemind.mailbox.identity.api.IdentityDescription import __IdentityDescriptionSerDer__
		return self.handleResult__(serder.ListSerDer(__IdentityDescriptionSerDer__()), response)
	def create (self, uid , identity ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.mailbox.identity.api.Identity import Identity
		from netbluemind.mailbox.identity.api.Identity import __IdentitySerDer__
		data = __IdentitySerDer__().encode(identity)

		queryParams = {    };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getIdentities (self):
		postUri = "";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.mailbox.identity.api.IdentityDescription import IdentityDescription
		from netbluemind.mailbox.identity.api.IdentityDescription import __IdentityDescriptionSerDer__
		return self.handleResult__(serder.ListSerDer(__IdentityDescriptionSerDer__()), response)
