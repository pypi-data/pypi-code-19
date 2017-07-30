import json
import urllib.parse
import warnings

import aiohttp
import pytest
from sovrin_common.constants import TARGET_NYM, ORIGIN, TXN_TYPE, \
    ATTRIB, NYM, TRUST_ANCHOR
from sovrin_common.txn_util import AddNym, AddAttr, STEWARD

from plenum.common.constants import TXN_ID, ROLE, IDENTIFIER, VERKEY, DATA
from plenum.common.signer_simple import SimpleSigner
from plenum.common.types import f, OPERATION
from plenum.common.util import randomString
from plenum.test.conftest import warnfilters as plenum_warnfilters
from sovrin_client_rest.test.constants import user_wallet_seed, \
    another_user_wallet_seed
from sovrin_client_rest.test.helper import TXN_URL, getResult, API_URL, NYM_URL
from sovrin_client_rest.util import buildWallet


def url_escape(nym):
    nym = urllib.parse.quote(nym)
    return nym.replace("/", "%2F")


def get_header_with_id(id):
    return {IDENTIFIER: id}

async def submit(id, post_body_data):
    with aiohttp.ClientSession() as session:
        async with session.post(TXN_URL, data=post_body_data,
                                headers=get_header_with_id(id)) as resp:
            t = await resp.text()
        jr = json.loads(t)
        return jr


async def submit_for_success(identifier, post_body_data):
    jr = await submit(identifier, post_body_data)
    reqId = jr[f.REQ_ID.nm]
    id = jr[IDENTIFIER]
    status, resp = await getResult(id, reqId)
    assert status == 200
    return resp


async def submit_nym(addedTrustAnchor, nym):
    nym = url_escape(nym)
    with aiohttp.ClientSession() as session:
        async with session.post(NYM_URL + "/{}".format(nym),
                                headers=get_header_with_id(
                                    addedTrustAnchor.defaultId)) as resp:
            t = await resp.text()
        jr = json.loads(t)
        return jr


async def submit_nym_for_success(addedTrustAnchor, dest):
    jr = await submit_nym(addedTrustAnchor, dest)
    reqId = jr[f.REQ_ID.nm]
    id = jr[IDENTIFIER]
    status, resp = await getResult(id, reqId)
    assert status == 200
    return resp


async def get_attrib(nym, attr, expectedStatus=200):
    with aiohttp.ClientSession() as session:
        nym = url_escape(nym)
        attr = url_escape(attr)
        getUrl = "{}/nym/{}/attr/{}".format(API_URL, nym, attr)
        headers = {'identifier': nym}
        async with session.get(getUrl, headers=headers) as resp:
            assert resp.status == expectedStatus
            t = await resp.text()
        jr = json.loads(t)
        return jr


async def get_all_attribs(nym, expectedStatus=200):
    with aiohttp.ClientSession() as session:
        nym = url_escape(nym)
        getUrl = "{}/nym/{}/attr".format(API_URL, nym)
        async with session.get(getUrl) as resp:
            assert resp.status == expectedStatus
            t = await resp.text()
        jr = json.loads(t)
        return jr


async def get_nym(nym, expectedStatus=204, expectedResp=None):
    with aiohttp.ClientSession() as session:
        nym = url_escape(nym)
        getUrl = "{}/nym/{}".format(API_URL, nym)
        async with session.get(getUrl) as resp:
            assert resp.status == expectedStatus
            t = await resp.text()
            if expectedResp:
                assert t == expectedStatus
            return resp.status, t


async def submit_attr(nym, attr):
    with aiohttp.ClientSession() as session:
        nym = url_escape(nym)
        async with session.post(NYM_URL + "/{}/{}".format(nym, attr),
                                headers=get_header_with_id(nym)) as resp:
            t = await resp.text()
        jr = json.loads(t)
        return jr


async def submit_attr_for_success(dest, attr):
    jr = await submit_attr(dest, attr)
    reqId = jr[f.REQ_ID.nm]
    nym = jr[TARGET_NYM]
    status, resp = await getResult(nym, reqId)
    assert status == 200
    return resp


async def get_txn_by_req_id(id, reqId):
    with aiohttp.ClientSession() as session:
        async with session.get("{}/{}".format(TXN_URL, reqId),
                               headers=get_header_with_id(id)) as resp:
            t = await resp.text()
        jr = json.loads(t)
        return jr


async def verify_token(nym, challenge, signature, expectedStatus=200):
    with aiohttp.ClientSession() as session:
        nym = url_escape(nym)
        challenge = url_escape(challenge)
        signature = url_escape(signature)
        url = "{}/nym/{}/verify?challenge={}&signature={}". \
            format(API_URL, nym, challenge, signature)
        async with session.get(url) as resp:
            assert resp.status == expectedStatus
            text = await resp.text()
        assert json.loads(text) == {"verified": True}


async def submit_unsuccessful_with_wrong_attr(dest, attr):
    jr = await submit_attr(dest, attr)
    return jr['error'] == "Invalid attribute: {}".format(attr)


@pytest.fixture(scope="module")
def genesisTxns():
    return [
        {   TXN_TYPE: NYM,
            TARGET_NYM: "aXMgYSBwaXQgYSBzZWVkLCBvciBzb21lcGluIGVsc2U=",
            TXN_ID: "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b",
            ROLE: STEWARD
        },
        {
            TXN_ID: '6b86b273ff34fce19d6b804eff5a3f57'
                    '47ada4eaa22f1d49c01e52ddb7875b4c',
            TXN_TYPE: NYM,
            TARGET_NYM: 'o7z4QmFkNB+mVkFI2BwX0Hdm1BGhnz8psWnKYIXWTaQ=',
            ROLE: TRUST_ANCHOR,
            f.IDENTIFIER.nm: "aXMgYSBwaXQgYSBzZWVkLCBvciBzb21lcGluIGVsc2U="
        }
    ]


def get_identifier(seed, identifier=None, name='user'):
    wallet = buildWallet(seed, identifier=identifier, name=name)
    return wallet.defaultId


def get_verkey(seed, identifier=None, name='user'):
    wallet = buildWallet(seed, identifier=identifier, name=name)
    return wallet._signerById(identifier).verkey


@pytest.fixture(scope="module")
def userNym():
    id, seed=user_wallet_seed
    return get_identifier(seed, id)


@pytest.fixture(scope="module")
def userNymVerKey():
    id, seed=user_wallet_seed
    return get_verkey(seed, id)


@pytest.fixture(scope="module")
def anotherUserNym():
    id, seed = another_user_wallet_seed
    return get_identifier(seed, id)


@pytest.fixture(scope="module")
def anotherUserNymVerKey():
    id, seed=another_user_wallet_seed
    return get_verkey(seed, id)


@pytest.fixture(scope="module")
def attribute():
    return json.dumps({"name": "Joe"})


# @pytest.fixture(scope="module")
# def anotherAttribute():
#     return json.dumps({"age": 21})
#
# @pytest.fixture(scope="module")
# def userNymAdded(cleanDir, client1Signer, looper, userNym,
#                  serverRunning):
#     op = AddNym(target=userNym)
#     result = looper.run(submitForSuccess(op))
#     assert result[TARGET_NYM] == userNym
#
# @pytest.fixture(scope="module")
# def anotherUserNymAdded(looper, serverRunning, anotherUserNym):
#     looper.run(submitNymForSuccess(anotherUserNym))
#

@pytest.fixture(scope="module")
def attributeAdded(serverRunning, looper, userNym, nym_added, attribute):
    post_body_data = AddAttr(target=userNym, attrData=attribute)
    result = looper.run(submit_for_success(userNym, post_body_data))
    assert result[TXN_TYPE] == ATTRIB


@pytest.fixture(scope="module")
def anotherAttributeAdded(userNymAdded, looper, serverRunning, userNym,
                          anotherAttribute):
    op = AddAttr(target=userNym, attrData=anotherAttribute)
    result = looper.run(submit_for_success(userNym, op))
    assert result[TXN_TYPE] == ATTRIB


@pytest.fixture('module')
def appSigner():
    return SimpleSigner()


@pytest.fixture('module')
def addAppVerKey(userNym, appSigner, looper):
    """
    Add app verkey as an attribute of the evernym
    """
    attr = json.dumps({"verKey": appSigner.verkey})
    op = AddAttr(target=userNym, attrData=attr)
    result = looper.run(submit_for_success(op))
    assert result[TXN_TYPE] == ATTRIB


# def testGetAllAttrTxn(userNymAdded, userNym, client1Signer, attribute,
#                       attributeAdded, anotherAttribute, anotherAttributeAdded,
#                       looper):
#     result = looper.run(getAllAttribs(userNym))
#     attr1 = json.loads(attribute)
#     attr2 = json.loads(anotherAttribute)
#     assert attr1 in result
#     assert attr2 in result
#
#
# def testVerifyToken(userNym, userNymAdded, appSigner, addAppVerKey, looper):
#     # 1. Generate a challenge
#     challenge = randomString(10)
#     # 2. use the signer to sign the challenge with the private key.
#     signature = appSigner.sign(challenge)
#     # 3. pass in the public key for verification
#     looper.run(verifyToken(userNym, challenge, signature))
#
#


@pytest.fixture(scope="session")
def warnfilters():
    def _():
        plenum_warnfilters()()
        warnings.filterwarnings('ignore', category=DeprecationWarning, module='aiohttp\.client', message='Use async with instead')
        warnings.filterwarnings('ignore', category=ResourceWarning, module='aiohttp\.web', message='loop argument is deprecated')
        # TODO: Need to change below line
        warnings.filterwarnings('ignore', category=ResourceWarning, module='.*', message='.*')
    return _


def test_get_unadded_nym_when_node_pool_is_not_running(prerequisite,
        serverRunningWithoutNodePoolRunning, userNym, looper):
    looper.run(get_nym(userNym, expectedStatus=504))


def test_get_unadded_nym(prerequisite, serverRunning, looper, userNym):
    looper.run(get_nym(userNym, expectedStatus=404))


def add_nym(looper, identifier, userNym, userNymVerKey):
    post_body_data = AddNym(target=userNym)
    post_body_data[VERKEY] = userNymVerKey
    result = looper.run(submit_for_success(identifier, post_body_data))
    assert result[TXN_TYPE] == NYM


@pytest.fixture(scope="module")
def nym_added(prerequisite, serverRunning, looper, addedTrustAnchor,
              userNym, userNymVerKey):
    add_nym(looper, addedTrustAnchor.defaultId, userNym, userNymVerKey)


@pytest.fixture(scope="module")
def another_nym_added(prerequisite, serverRunning, looper, addedTrustAnchor,
                      anotherUserNym, anotherUserNymVerKey):
    add_nym(looper, addedTrustAnchor.defaultId, anotherUserNym, anotherUserNymVerKey)


def test_add_nym(nym_added):
    pass


def test_add_nym_again(prerequisite, serverRunning, looper, addedTrustAnchor,
                       userNym, userNymVerKey, nym_added):
    add_nym(looper, userNym, userNym, userNymVerKey)


def test_get_added_nym(nym_added, looper, userNym):
    looper.run(get_nym(userNym, expectedStatus=200))


def test_add_txn_without_type(serverRunning, looper):
    op = {TARGET_NYM: "SomeRandomNym6"}
    result = looper.run(submit("SomeRandomNym6", op))
    assert "'{}' should be present in request arguments".format(TXN_TYPE) in result['error']


# def test_get_txn_by_req_id(prerequisite, serverRunning, looper, addedTrustAnchor):
#     nym = get_identifier(seed=randomString(32))
#     result = looper.run(submit_nym_for_success(addedTrustAnchor, nym))
#     res = looper.run(get_txn_by_req_id(addedTrustAnchor.defaultId, result[f.REQ_ID.nm]))
#     assert res is not None


def test_add_attrib(prerequisite, serverRunning, looper, attributeAdded):
    pass


def test_add_attrib_only_if_user_exists(prerequisite, serverRunning, looper):
    op = AddAttr(target="SomeUnAddedDest", attrData=json.dumps({"name": "Joe"}))
    op[IDENTIFIER] = "SomeUnAddedDest"
    result = looper.run(submit("SomeUnAddedDest", op))
    assert "{} should be added before adding attribute for it".\
               format(TARGET_NYM) in result['error']


def test_get_attr_txn(nym_added, looper, userNym, attributeAdded, attribute):
    attr = json.loads(attribute)
    attrName = list(attr.keys())[0]
    result = looper.run(get_attrib(userNym, attrName))
    assert attr == json.loads(result[DATA])


def test_nym_from_path_param_with_wrong_attr(prerequisite, serverRunning, looper,
                                             anotherUserNym, another_nym_added):
    assert looper.run(submit_unsuccessful_with_wrong_attr(anotherUserNym,
                                                          "SomeRandomAttribute"))


def test_nym_from_path_param_with_attr(prerequisite, serverRunning, looper,
                                       attribute, anotherUserNym, another_nym_added):
    looper.run(submit_attr_for_success(anotherUserNym, attribute))

