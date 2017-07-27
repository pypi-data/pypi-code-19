class SiaHostDB(object):
    """
    The HostDB maintains a database of all hosts known to the network. The database identifies hosts by their public key and keeps track of metrics such as price.
    """
    def __init__(self, scpy):
        self.scpy = scpy

    def active(self, numhosts=None):
        """
        Lists all of the active hosts known to the renter, sorted by preference.

        :param numhosts: Number of hosts to return. The actual number of hosts returned may be less if there are insufficient active hosts. Optional, the default is all active hosts.
        :type numhosts: int
        :return: List of dicts with host information, sorted by preference
        """
        if numhosts:
            return self.scpy.get_api('/hostdb/active', params={'numhosts': numhosts})['hosts']
        else:
            return self.scpy.get_api('/hostdb/active')['hosts']

    @property
    def all(self):
        """
        List with all of the hosts known to the renter. Hosts are not guaranteed to be in any particular order, and the order may change in subsequent calls.
        """
        return self.scpy.get_api('/hostdb/all')['hosts']

    def host(self, pubkey):
        """
        Fetches detailed information about a particular host, including metrics regarding the score of the host within the database. It should be noted that each renter uses different metrics for selecting hosts, and that a good score on in one hostdb does not mean that the host will be successful on the network overall.

        :param pubkey: The public key of the host. Each public key identifies a single host.
        :type pubkey: str
        :return: Dict with detailed host information
        :raises: SiaError if no host corresponding to pubkey was found
        """
        return self.scpy.get_api(f'/hostdb/hosts/{pubkey}')