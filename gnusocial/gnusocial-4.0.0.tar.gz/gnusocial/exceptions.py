class ServerURLError(Exception):
    def __init__(self, server_url):
        self.server_url = server_url
        super().__init__(Exception)

    def __repr__(self):
        return 'ServerURLError(%r)' % self.server_url

    def __str__(self):
        return 'Invalid server URL %s' % self.server_url
