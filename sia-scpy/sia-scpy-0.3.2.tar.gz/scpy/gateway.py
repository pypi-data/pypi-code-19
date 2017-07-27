class SiaGateway(object):
    """
    The gateway maintains a peer to peer connection to the network and provides a method for calling RPCs on connected peers. The gateway's API endpoints expose methods for viewing the connected peers, manually connecting to peers, and manually disconnecting from peers. The gateway may connect or disconnect from peers on its own.
    """
    def __init__(self, scpy):
        self.scpy = scpy

    def __call__(self):
        """
        Returns information about the gateway, including the list of connected peers

        :return: Dict with information about the gateway
        """
        return self.scpy.get_api('/gateway')

    def connect(self, address):
        """
        Connects the gateway to a peer. The peer is added to the node list if it is not already present

        :param address: The address of the peer to connect to. It should be a reachable ip address and port number, of the form 'IP:port'. IPv6 addresses must be enclosed in square brackets.
        :type address: str
        :return: True if action succeeded
        :raises: SiaError if action was unsuccessful
        """
        return self.scpy.post_api(f'/gateway/connect/{address}')

    def disconnect(self, address):
        """
        Disconnects the gateway from a peer. The peer remains in the node list. Disconnecting from a peer does not prevent the gateway from automatically connecting to the peer in the future.

        :param address: The address of the peer to disconnect from. It should comply to the same restrictions as the connect() method.
        :type address: str
        :return: True if action succeeded
        :raises: SiaError if action was unsuccessful
        """
        return self.scpy.post_api(f'/gateway/disconnect/{address}')
