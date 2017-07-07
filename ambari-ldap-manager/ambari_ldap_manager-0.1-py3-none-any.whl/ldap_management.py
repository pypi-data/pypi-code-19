import requests
from requests.auth import HTTPBasicAuth
import json

# curl -u admin:admin -H "X-Requested-By: ambari" -X GET http://localhost.com:8080/api/v1/groups/your-ldap-group
# curl -i -uadmin:admin -H 'X-Requested-By: ambari' -X POST -d '[{"Event": {"specs": [{"principal_type": "users", "sync_type": "specific", "names": "bill,jenny,mike"},{"principal_type":"groups","sync_type":"specific", "names": "group1,group2"}]}}]' http://localhost:8080/api/v1/ldap_sync_events

class LdapManager(object):
	def __init__(self, url, api, username, password):
		self.ambari_url = url
		self.ambari_api = api
		self.username = username
		self.password = password

		self.set_namenode()
		self.set_hdfs_api()

		self.xheader = {"X-Requested-By": "HttpRequest"}

	def get_all_users(self):
		return requests.get(self.ambari_url + self.ambari_api + "/users", auth=HTTPBasicAuth(self.username, self.password))

	def get_all_groups(self):
		return requests.get(self.ambari_url + self.ambari_api + "/groups", auth=HTTPBasicAuth(self.username, self.password))

	def get_all_events(self):
		return requests.get(self.ambari_url + self.ambari_api + "/ldap_sync_events", auth=HTTPBasicAuth(self.username, self.password))

	def get_user(self, user):
		return requests.get(self.ambari_url + self.ambari_api + "/users/" + user, auth=HTTPBasicAuth(self.username, self.password))

	def delete_user(self, user):
		return requests.delete(self.ambari_url + self.ambari_api + "/users/" + user, auth=HTTPBasicAuth(self.username, self.password), headers=self.xheader)

	def get_group(self, group):
		return requests.get(self.ambari_url + self.ambari_api + "/groups/" + group, auth=HTTPBasicAuth(self.username, self.password))

	def delete_group(self, group):
		return requests.delete(self.ambari_url + self.ambari_api + "/groups/" + group, auth=HTTPBasicAuth(self.username, self.password), headers=self.xheader)

	def get_event(self, event):
		return requests.get(self.ambari_url + self.ambari_api + "/ldap_sync_events/" + event, auth=HTTPBasicAuth(self.username, self.password))

	def sync_user(self, user):
		# curl -i -uadmin:admin -H 'X-Requested-By: ambari' 
		# 	-X POST -d '[{"Event": {"specs": 
		# 		[{"principal_type": "users", "sync_type": "specific", "names": "bill,jenny,mike"},
		# 		 {"principal_type":"groups","sync_type":"specific", "names": "group1,group2"}]
		# 		 }}]' 
		# 		 http://localhost:8080/api/v1/ldap_sync_events
		self.hdfs_home_mkdir(user)
		self.hdfs_home_chown(user)

		payload = {"Event": {"specs": 
						[{"principal_type":"users","sync_type":"specific", "names": user}]
				 }}
		return requests.post(self.ambari_url + self.ambari_api + "/ldap_sync_events", data=json.dumps(payload), headers=self.xheader, auth=HTTPBasicAuth(self.username, self.password))

	def sync_group(self, group):
		# curl -i -uadmin:admin -H 'X-Requested-By: ambari' 
		# 	-X POST -d '[{"Event": {"specs": 
		# 		[{"principal_type": "users", "sync_type": "specific", "names": "bill,jenny,mike"},
		# 		 {"principal_type":"groups","sync_type":"specific", "names": "group1,group2"}]
		# 		 }}]' 
		# 		 http://localhost:8080/api/v1/ldap_sync_events
		payload = {"Event": {"specs": 
						[{"principal_type":"groups","sync_type":"specific", "names": group}]
				 }}

		group_users = self.get_group(group).json()

		for g in range(len(group_users['members'])):
			user = group_users['members'][g]['MemberInfo']['user_name']
			self.sync_user(user)

		return requests.post(self.ambari_url + self.ambari_api + "/ldap_sync_events", data=json.dumps(payload), headers=self.xheader, auth=HTTPBasicAuth(self.username, self.password))

	def get_cluster_name(self):
		return requests.get(self.ambari_url + self.ambari_api + "/clusters/", auth=HTTPBasicAuth(self.username, self.password)).json()["items"][0]["Clusters"]["cluster_name"]

	def set_namenode(self, retry=0):
		# gets the current namenode from ambari and sets it
		# http://{HOST}:8080/api/v1/clusters/{CLUSTER_NAME}/host_components?HostRoles/component_name=NAMENODE&metrics/dfs/FSNamesystem/HAState=active
		#
		# param: retry <None> -- Sometimes Ambari responds incorrectly. Gets fixed each time with another call.
		
		try:
			cluster_name = self.get_cluster_name()
			HA_url = "/clusters/" + cluster_name + "/host_components?HostRoles/component_name=NAMENODE&metrics/dfs/FSNamesystem/HAState=active"
			res = requests.get(self.ambari_url + self.ambari_api + HA_url, auth=HTTPBasicAuth(self.username, self.password)).json()
		
			self.active_namenode = res["items"][0]["HostRoles"]["host_name"]
		except IndexError:
			if retry < 3: 
				self.set_namenode(retry+1)
			else:
				self.active_namenode = None

	def set_hdfs_api(self):
		self.hdfs_api = "http://" + self.active_namenode + ":50070/webhdfs/v1"


	def hdfs_home_mkdir(self, user):
		# curl -i -X PUT "http://localhost:50070/webhdfs/v1/user/abc?user.name=hdfs&doas=hdfs&op=MKDIRS"
		path = "/user/" + user
		data = {
			"user.name": "hdfs",
			"doas": "hdfs",
			"op": "MKDIRS"
		}

		url = self.hdfs_api + path

		return requests.put(url, headers=self.xheader, params=data)

	def hdfs_home_rmdir(self, user):
		# curl -i -X DELETE "http://localhost:50070/webhdfs/v1/user/abc?user.name=hdfs&doas=hdfs&op=DELETE"
		path = "/user/" + user

		data = {
			"user.name": "hdfs",
			"doas": "hdfs",
			"op": "DELETE"
		}

		url = self.hdfs_api + path

		return requests.delete(url, headers=self.xheader, params=data)

	def hdfs_home_chown(self, user):
		# curl -i -X PUT "http://localhost:50070/webhdfs/v1/user/abc?user.name=hdfs&doas=hdfs&op=SETOWNER&owner=abc"
		path = "/user/" + user

		data = {
			"user.name": "hdfs",
			"doas": "hdfs",
			"op": "SETOWNER",
			"owner": user
		}

		url = self.hdfs_api + path

		return requests.put(url, headers=self.xheader, params=data)


if __name__ == '__main__':
	pass



