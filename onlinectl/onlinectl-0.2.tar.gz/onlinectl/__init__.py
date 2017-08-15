#!/usr/bin/env python
import requests
import slumber

class OnlineCtl():
    """
        PythonClass to interact with online.net API
    """

    def __init__(self, token):
        """
            Initialize connexion with Online API
        """
        api_session = requests.session()
        self.token = 'Bearer ' + token
        self.api_url = 'https://api.online.net/api/v1'
        api_session.headers['Authorization'] = self.token
        self.api = slumber.API(self.api_url, session=api_session, 
                append_slash=False)
    
    def get_lists_of_servers(self):
        servers_list = []
        for i in self.api.server.get():
            servers_list.append(self.api.server(i).get())
        self.servers_list = servers_list
        return(servers_list)
    
    def get_available_os(self, server_id):
        try:
            int(server_id)
        except Exception as e:
            print("server_id must be an integer : {}".format(e))
        os_list = self.api.server.operatingSystems(server_id).get()
        return os_list

    def get_sshkeys(self):
        ssh_keys = self.api.user.key.ssh.get()
        return ssh_keys
    
    def put_sshkeys(self,pubkey):
        pass

    def install_server(self, server_id, os_id, hostname, user_login, 
            user_password, root_password, pannel_password, ssh_keys):
        self.api.server.install(server_id).post({'os_id':os_id, 'hostname': hostname, 
            'user_login': user_login, 'user_password': user_password, 
            'root_password': root_password, 'pannel_password': pannel_password, 'ssh_keys':ssh_keys})
