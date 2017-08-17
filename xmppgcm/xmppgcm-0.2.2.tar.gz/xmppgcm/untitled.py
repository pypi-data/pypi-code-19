
    @property
    def connection_draining(self):
        """ This is a fix to the mispelling connecton_draining,
        "i" is missing, but this is for not breaking the already
        working implementations of the module. """

        return self.connecton_draining

    @connection_draining.setter
    def connection_draining(self, value):
        self.connecton_draining = value



    @property
    def is_error(self):
        return 'error' in self.data

    @property
    def error_description(self):
        description = self.data.get('error_description', '')
        error = self.data.get('error', '')
        if description:
            return ' %s: %s' % (error, description)
        else:
            return error