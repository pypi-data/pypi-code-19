
class Client(object):

    def __init__(
            self, authurl=None, user=None, key=None, preauthurl=None,
            preauthtoken=None, tenant_name=None, os_options=None,
            insecure=False
    ):
        """
        :param authurl: authentication URL
        :param user: user name to authenticate as
        :param key: key/password to authenticate with
        :param retries: Number of times to retry the request before failing
        :param preauthurl: storage URL (if you have already authenticated)
        :param preauthtoken: authentication token (if you have already
                             authenticated) note authurl/user/key/tenant_name
                             are not required when specifying preauthtoken
        :param tenant_name: The tenant/account name, required when connecting
                            to an auth 2.0 system.
        :param os_options: The OpenStack options which can have tenant_id,
                           auth_token, service_type, endpoint_type,
                           tenant_name, block_storage_url, region_name,
                           service_username, service_project_name, service_key
        :param insecure: Allow to access servers without checking SSL certs.
                         The server's certificate will not be verified.
        """
        self.authurl = authurl
        self.user = user
        self.key = key
        self.http_conn = None
        self.attempts = 0
        self.os_options = dict(os_options or {})
        if tenant_name:
            self.os_options['tenant_name'] = tenant_name
        if preauthurl:
            self.os_options['block_storage_url'] = preauthurl

        self.url = preauthurl or self.os_options.get('block_storage_url')
        self.token = preauthtoken or self.os_options.get('auth_token')

        if self.os_options.get('service_username', None):
            self.service_auth = True
        else:
            self.service_auth = False
        self.service_token = None
        self.insecure = insecure

    def access_list(self, export_id_or_path):
        raise NotImplementedError

    def access_delete(self, export_id_or_path, access_id):
        raise NotImplementedError

    def access_create(self, export_id_or_path, permission, host):
        raise NotImplementedError

    def export_create(self, quota, categoria, resource_id):
        raise NotImplementedError

    def export_delete(self, export_id_or_path):
        raise NotImplementedError

    def quota_get(self, export_id):
        raise NotImplementedError

    def quota_post(self, export_id, size):
        raise NotImplementedError

    def jobs_get(self, job_id):
        raise NotImplementedError

    def snapshot_delete(self, export_id_or_path, snapshot_id):
        raise NotImplementedError

    def snapshot_create(self, export_id_or_path):
        raise NotImplementedError

    def snapshot_restore(self, export_id_or_path, snapshot_id):
        raise NotImplementedError
