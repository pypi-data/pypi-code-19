import json
import aiohttp
from stp_core.network.port_dispenser import genHa

from plenum.test.test_stack import StackedTester
from sovrin_client_rest.client_storage import ClientStorage
from sovrin_client.test.helper import TestClient as TestSovrinClient
from sovrin_client_rest.util import getConfig


config = getConfig()


def getTxnUrl(identifier, reqId):
    return "{}/identifier/{}/request/{}".format(TXN_URL, identifier, reqId)


def checkTxnProcessed(identifier, reqId):
    jr = getResult(identifier, reqId)
    assert "txnId" in jr


async def getResult(identifier, reqId):
    getUrl = getTxnUrl(identifier, reqId)
    with aiohttp.ClientSession() as session:
        async with session.get(getUrl) as resp:
            t = await resp.text()
        jr = None
        if 200 <= resp.status < 300:
            jr = json.loads(t)
        return resp.status, jr


def getClientLastReqId(identifier):
    cs = ClientStorage(identifier)
    return cs.getLastReqId()


port = genHa()[1]
serverAddr = ("127.0.0.1", port)
config.serverAddr = serverAddr

API_URL = "http://{}:{}".format(*config.serverAddr)
TXN_URL = "{}/txn".format(API_URL)
NYM_URL = "{}/nym".format(API_URL)
clientId = "client1"


class TestClient(TestSovrinClient, StackedTester):
    pass
