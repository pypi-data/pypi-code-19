import os

from sovrin_client.test.conftest import *
from sovrin_client_rest.client_storage import ClientStorage
from sovrin_client_rest.rest_server import RestServer
from sovrin_client_rest.test.constants import user_wallet_seed, trust_anchor_seed, \
    unadded_dest, another_user_wallet_seed
from sovrin_client_rest.util import getConfig as restConf, buildWallet


@pytest.fixture(scope='module', autouse=True)
def cleanDir(tdir):
    ClientStorage.basePath = tdir
    print("Setting ClientStorage to use base path of {}".format(tdir))
    return tdir


@pytest.fixture(scope="module")
def restServerConfig(tdir):
    conf = restConf()
    conf.baseDataDir = tdir
    return conf


@pytest.fixture(scope="module")
def client1BaseDir(config):
    return ClientStorage.getDataLocation(config.clientName)


@pytest.fixture(scope="module")
def client1Signer():
    return SimpleSigner(seed=b'g034OTmx7qBRtywvCbKhjfALHnsdcJpl')


@pytest.fixture(scope="module")
def clientAndWallet1(client1Signer, looper, nodeSet, tdir, up):
    client, wallet = genTestClient(nodeSet, tmpdir=tdir, usePoolLedger=True)
    wallet = Wallet(client.name)
    wallet.addIdentifier(signer=client1Signer)
    return client, wallet


@pytest.fixture(scope="module")
def pclient1(config, clientAndWallet1, tdir, nodeSet, looper, up):

    client, _ = clientAndWallet1
    for node in nodeSet:
        node.whitelistClient(client.name)
    looper.add(client)
    looper.run(client.ensureConnectedToNodes())
    return client


@pytest.fixture(scope="module")
def restServerStarted(looper, restServerConfig):
    rs = RestServer(restServerConfig, looper)
    looper.runFor(5)
    return rs


@pytest.fixture(scope="module")
def serverRunningWithoutNodePoolRunning(restServerStarted):
    return restServerStarted


@pytest.fixture(scope="module")
def serverRunning(nodeSet, restServerStarted):
    return restServerStarted


@pytest.fixture(scope="module")
def prerequisite(restServerConfig, tconf, tdirWithPoolTxns, tdirWithDomainTxns):
    global clientConfig
    global restSvrConfig

    clientConfig = tconf
    restSvrConfig = restServerConfig

    seedFileDir = os.path.expanduser(
        os.path.join(restServerConfig.baseDataDir, restServerConfig.seedFileDir))
    os.mkdir(seedFileDir)
    for id, seed in [user_wallet_seed, trust_anchor_seed, unadded_dest,
                     another_user_wallet_seed]:
        wallet = buildWallet(seed, identifier=id, name=id)
        seedFilePath = '{}/{}'.format(seedFileDir, wallet.defaultId)
        with open(seedFilePath, 'w+') as seed_file:
            seed_file.write(seed)