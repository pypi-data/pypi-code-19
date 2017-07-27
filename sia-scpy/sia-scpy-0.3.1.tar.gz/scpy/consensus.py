class SiaConsensus(object):
    """
    The consensus set manages everything related to consensus and keeps the blockchain in sync with the rest of the network. The consensus set's API endpoint returns information about the state of the blockchain.
    """
    def __init__(self, scpy):
        self.scpy = scpy

    @property
    def synced(self):
        """
        True if the consensus set is synced with the network, i.e. it has downloaded the entire blockchain.
        """
        return self.scpy.get_api('/consensus')['synced']

    @property
    def height(self):
        """
        Number of blocks preceding the current block.
        """
        return self.scpy.get_api('/consensus')['height']

    @property
    def currentblock(self):
        """
        Hash of the current block.
        """
        return self.scpy.get_api('/consensus')['currentblock']

    @property
    def target(self):
        """
        An immediate child block of this block must have a hash less than this target for it to be valid.
        """
        return self.scpy.get_api('/consensus')['target']

    @property
    def difficulty(self):
        """
        The difficulty of the current block target
        """
        return int(self.scpy.get_api('/consensus')['difficulty'])
