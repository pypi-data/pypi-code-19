import ldap_management_server 
from ldap_management import LdapManager
from flask import Flask
import uuid
import sys

def main(args=None):
	if args is None:
		args = sys.argv
	if len(args) != 4:
		print("""Ambari LDAP Manager should be invokes as follows:
		python -m ambari-ldap-manager <http://ambari-host:8080> <username> <password>
			""")
		sys.exit(1)
	else:
		ambari_url = args[1]
		username = args[2]
		password = args[3]

		ldap_management_server.main(ambari_url, username, password)

if __name__ == "__main__":
	main()