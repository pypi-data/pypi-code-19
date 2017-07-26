from opfront.client import OpfrontClient
from opfront.order import OrderResource
from opfront.product import ProductResource
from opfront.resource import OpfrontResource
from opfront.store import StoreResource
from opfront.user import UserResource


class OpfrontSession(object):

    """
    OpfrontSession defines the set of resources available from the Opfront API.
    Can be used as a standard object as and as a context manager.

    Args:
        email (str): Email with which to login
        password (str): Password associated with the email
    """

    def __init__(self, email, password, **kwargs):
        client = OpfrontClient(email, password, **kwargs)

        # Resource definition
        self.banner = OpfrontResource('/banners', client)
        self.spectacle = OpfrontResource('/spectacles', client)
        self.store = StoreResource('/stores', client)
        self.product = ProductResource('/products', client)
        self.order = OrderResource('/orders', client)
        self.user = UserResource('/users', client)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
