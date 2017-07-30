import importlib
import importlib.util

from sovrin_common.config_util import getInstalledConfig

from plenum.common.util import randomString
from sovrin_client.client.wallet.wallet import Wallet


def getConfig():
    try:
        config = getInstalledConfig("sovrin_client_rest", "sovrin_client_rest_config.py")
    except FileNotFoundError:
        config = importlib.import_module("sovrin_client_rest.config_example")
    return config


def buildWallet(seed, identifier=None, name=None):
    wallet = Wallet(name or randomString(6))
    wallet.addIdentifier(seed=seed.encode('utf-8'), identifier=identifier)
    return wallet