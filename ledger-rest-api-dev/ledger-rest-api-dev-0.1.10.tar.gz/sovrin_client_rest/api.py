#! /usr/bin/env python3

import os

from sovrin_client_rest.rest_server import RestServer
from stp_core.loop.looper import Looper

from sovrin_client_rest.util import getConfig
from sovrin_client.client.client import Client


config = getConfig()


async def run(looper):
    RestServer(config, looper, serverAddr=config.serverAddr)


def run_server():
    with Looper(debug=True) as looper:
        client_name = config.clientName
        base_dir_path = os.path.expanduser(config.baseDataDir)
        if not os.path.exists(base_dir_path):
            os.makedirs(base_dir_path)
        client_address = config.clientToPoolAddr
        client = Client(client_name,
                        nodeReg=None,
                        ha=client_address,
                        basedirpath=base_dir_path)
        looper.add(client)
        looper.run(run(looper))
        looper.loop.run_forever()


if __name__ == "__main__":
    run_server()
