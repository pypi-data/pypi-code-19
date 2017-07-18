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

class IMailboxes(BaseEndpoint):
	def __init__(self, apiKey, url ,domainUid ):
		self.url = url
		self.apiKey = apiKey
		self.base = url +'/mailboxes/{domainUid}'
		self.domainUid_ = domainUid
		self.base = self.base.replace('{domainUid}',domainUid)

	def update (self, uid , mailbox ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.mailbox.api.Mailbox import Mailbox
		from netbluemind.mailbox.api.Mailbox import __MailboxSerDer__
		data = __MailboxSerDer__().encode(mailbox)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def byName (self, name ):
		postUri = "/_byname";
		data = None
		queryParams = {  'name': name   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.mailbox.api.Mailbox import Mailbox
		from netbluemind.mailbox.api.Mailbox import __MailboxSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(__ItemValueSerDer__(__MailboxSerDer__()), response)
	def delete (self, uid ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def setMailboxFilter (self, mailboxUid , filter ):
		postUri = "/{mailboxUid}/_filter";
		data = None
		postUri = postUri.replace("{mailboxUid}",mailboxUid);
		from netbluemind.mailbox.api.MailFilter import MailFilter
		from netbluemind.mailbox.api.MailFilter import __MailFilterSerDer__
		data = __MailFilterSerDer__().encode(filter)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getUnreadMessagesCount (self):
		postUri = "/_unread";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.INT, response)
	def setMailboxAccessControlList (self, mailboxUid , accessControlEntries ):
		postUri = "/{mailboxUid}/_acls";
		data = None
		postUri = postUri.replace("{mailboxUid}",mailboxUid);
		from netbluemind.core.container.model.acl.AccessControlEntry import AccessControlEntry
		from netbluemind.core.container.model.acl.AccessControlEntry import __AccessControlEntrySerDer__
		data = serder.ListSerDer(__AccessControlEntrySerDer__()).encode(accessControlEntries)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def byEmail (self, email ):
		postUri = "/_byemail";
		data = None
		queryParams = {  'email': email   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.mailbox.api.Mailbox import Mailbox
		from netbluemind.mailbox.api.Mailbox import __MailboxSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(__ItemValueSerDer__(__MailboxSerDer__()), response)
	def create (self, uid , mailbox ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.mailbox.api.Mailbox import Mailbox
		from netbluemind.mailbox.api.Mailbox import __MailboxSerDer__
		data = __MailboxSerDer__().encode(mailbox)

		queryParams = {    };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def byRouting (self, email ):
		postUri = "/_byRouting";
		data = None
		queryParams = {  'email': email   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.ListSerDer(serder.STRING), response)
	def checkAll (self):
		postUri = "/_check-all";
		data = None
		queryParams = {  };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.task.api.TaskRef import TaskRef
		from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
		return self.handleResult__(__TaskRefSerDer__(), response)
	def multipleGet (self, uids ):
		postUri = "/_mget";
		data = None
		data = serder.ListSerDer(serder.STRING).encode(uids)

		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.mailbox.api.Mailbox import Mailbox
		from netbluemind.mailbox.api.Mailbox import __MailboxSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__MailboxSerDer__())), response)
	def checkAndRepair (self, uid ):
		postUri = "/{uid}/_check-and-repair";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.task.api.TaskRef import TaskRef
		from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
		return self.handleResult__(__TaskRefSerDer__(), response)
	def getMailboxFilter (self, mailboxUid ):
		postUri = "/{mailboxUid}/_filter";
		data = None
		postUri = postUri.replace("{mailboxUid}",mailboxUid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.mailbox.api.MailFilter import MailFilter
		from netbluemind.mailbox.api.MailFilter import __MailFilterSerDer__
		return self.handleResult__(__MailFilterSerDer__(), response)
	def getMailboxAccessControlList (self, mailboxUid ):
		postUri = "/{mailboxUid}/_acls";
		data = None
		postUri = postUri.replace("{mailboxUid}",mailboxUid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.acl.AccessControlEntry import AccessControlEntry
		from netbluemind.core.container.model.acl.AccessControlEntry import __AccessControlEntrySerDer__
		return self.handleResult__(serder.ListSerDer(__AccessControlEntrySerDer__()), response)
	def check (self, uid ):
		postUri = "/{uid}/_check";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.task.api.TaskRef import TaskRef
		from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
		return self.handleResult__(__TaskRefSerDer__(), response)
	def list (self):
		postUri = "/_list";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.mailbox.api.Mailbox import Mailbox
		from netbluemind.mailbox.api.Mailbox import __MailboxSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__MailboxSerDer__())), response)
	def setDomainFilter (self, filter ):
		postUri = "/_filter";
		data = None
		from netbluemind.mailbox.api.MailFilter import MailFilter
		from netbluemind.mailbox.api.MailFilter import __MailFilterSerDer__
		data = __MailFilterSerDer__().encode(filter)

		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getMailboxQuota (self, uid ):
		postUri = "/{uid}/_quota";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.mailbox.api.MailboxQuota import MailboxQuota
		from netbluemind.mailbox.api.MailboxQuota import __MailboxQuotaSerDer__
		return self.handleResult__(__MailboxQuotaSerDer__(), response)
	def getComplete (self, uid ):
		postUri = "/{uid}/complete";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.mailbox.api.Mailbox import Mailbox
		from netbluemind.mailbox.api.Mailbox import __MailboxSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(__ItemValueSerDer__(__MailboxSerDer__()), response)
	def getDomainFilter (self):
		postUri = "/_filter";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.mailbox.api.MailFilter import MailFilter
		from netbluemind.mailbox.api.MailFilter import __MailFilterSerDer__
		return self.handleResult__(__MailFilterSerDer__(), response)
	def byType (self, email ):
		postUri = "/_byType";
		data = None
		queryParams = {  'email': email   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.ListSerDer(serder.STRING), response)
	def checkAndRepairAll (self):
		postUri = "/_check-and-repair-all";
		data = None
		queryParams = {  };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.task.api.TaskRef import TaskRef
		from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
		return self.handleResult__(__TaskRefSerDer__(), response)
