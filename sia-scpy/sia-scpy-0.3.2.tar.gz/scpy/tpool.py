class SiaTPool(object):
    """
    The transaction pool provides endpoints for getting transactions currently in the transaction pool and submitting transactions to the transaction pool.
    """
    def __init__(self, scpy):
        self.scpy = scpy

    @property
    def fee(self):
        """
        Returns the minimum and maximum estimated fees expected by the transaction pool.

        :return: Dict with maximum and minimum fees in hastings
        """
        return self.scpy.get_api('/tpool/fee')

    def get_raw(self, id):
        """
        Returns the ID for the requested transaction and its raw encoded parents and transaction data.

        :param id: Id of the transaction
        :return: Dict with raw, base64 encoded transaction data for the transaction and its parents
        """
        return self.scpy.get_api(f'/tpool/raw/{id}')

    def submit_raw(self, parents, transaction):
        """
        Submits a raw transaction to the transaction pool, broadcasting it to the transaction pool's peers.

        :param parents: Raw base64 encoded transaction parents
        :param transaction: Raw base64 encoded transaction
        :return: True if action succeeded
        :raises: SiaError if action was unsuccessful
        """
        return self.scpy.post_api('/tpool/raw', data={'parents': parents, 'transaction': transaction})
