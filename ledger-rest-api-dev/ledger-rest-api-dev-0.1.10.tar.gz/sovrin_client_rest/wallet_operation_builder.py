import os
from typing import Dict

from plenum.common.constants import IDENTIFIER, TYPE, TARGET_NYM, VERKEY, \
    ROLE, RAW, ENC, HASH, NAME
from plenum.common.util import randomString
from sovrin_client.client.wallet.attribute import Attribute, LedgerStore
from sovrin_client_rest.exceptions import SeedFileNotFound
from sovrin_client_rest.test.constants import default_seed

from sovrin_client_rest.util import getConfig as restServerConfig, buildWallet
from sovrin_common.identity import Identity
from sovrin_common.transactions import SovrinTransactions
from stp_core.common.log import getlogger

logger = getlogger()

wallets = {}  # Dict[Identifier, wallet]

rest_server_config = restServerConfig()

OP_DATA = "OP_DATA"


def build_wallet_from_seed_file(identifier, op_type):
    seedFileDir = os.path.expanduser(os.path.join(rest_server_config.baseDataDir,
                                                  rest_server_config.seedFileDir))
    seedFilePath = '{}/{}'.format(seedFileDir, identifier)

    # if seed file is available, read seed from it
    seed = None
    if os.path.isfile(seedFilePath):
        logger.info('seed file found for identifier: {}'.format(identifier))
        try:
            with open(seedFilePath, mode='r+') as file:
                seed = file.read().strip(' \t\n\r')
        except OSError as e:
            logger.warn('Error occurred while reading seed file: '
                        'error:{}'.format(e))
            raise e
    elif op_type in (SovrinTransactions.GET_NYM.value, SovrinTransactions.GET_ATTR.value):
        seed = default_seed
    else:
        raise SeedFileNotFound('No seed file present at path: {}'.format(seedFilePath))
    print("#### seed: {}".format(seed))
    wallet = buildWallet(seed, identifier=identifier, name=identifier)
    wallets[identifier] = wallet
    return wallet


def get_req_identifier(request):
    return request.get(IDENTIFIER)


def get_wallet_by_identifier(identifier, op_type):
    wallet = wallets.get(identifier)
    if wallet:
        return wallet
    else:
        return build_wallet_from_seed_file(identifier, op_type)


async def get_prepared_req(identifier, req_data: Dict):

    if req_data.get(OP_DATA):
        op_data = req_data.get(OP_DATA)
        op_type = op_data.get(TYPE)

        wallet = get_wallet_by_identifier(identifier, op_type)

        if op_type == SovrinTransactions.NYM.value:
            idy = Identity(op_data[TARGET_NYM],
                           verkey=op_data.get(VERKEY, None),
                           role=op_data.get(ROLE, None))
            wallet.addTrustAnchoredIdentity(idy)
            req_data = wallet.preparePending()[0]
        elif op_type == SovrinTransactions.GET_NYM.value:
            identity = Identity(identifier=wallet.defaultId)
            req_data = wallet.requestIdentity(identity, sender=wallet.defaultId)
        elif op_type == SovrinTransactions.ATTRIB.value:
            if op_data.get(RAW):
                data = op_data[RAW]
            elif op_data.get(ENC):
                data = op_data[ENC]
            elif op_data.get(HASH):
                data = op_data[HASH]
            else:
                raise RuntimeError('One of raw, enc, or hash are required.')
            attrib = Attribute(randomString(5), data,
                               wallet.defaultId,
                               dest=op_data[TARGET_NYM],
                               ledgerStore=LedgerStore.RAW)

            wallet.addAttribute(attrib)
            req_data = wallet.preparePending()[0]
        elif op_type == SovrinTransactions.GET_ATTR.value:
            attrib = Attribute(name=op_data[NAME],
                               value=None,
                               dest=op_data[TARGET_NYM],
                               ledgerStore=LedgerStore.RAW)
            req_data = wallet.requestAttribute(attrib, sender=wallet.defaultId)
    return req_data