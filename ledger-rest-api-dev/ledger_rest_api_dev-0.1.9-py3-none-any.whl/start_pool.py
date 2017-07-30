from tempfile import TemporaryDirectory

from stp_core.loop.looper import Looper
from sovrin_client_rest.util import getConfig
from sovrin_node.server.node import Node


def start():
    NODEREG = {
        'Alpha': ('127.0.0.1', 8001),
        'Beta': ('127.0.0.1', 8003),
        'Gamma': ('127.0.0.1', 8005),
        'Delta': ('127.0.0.1', 8007)
    }

    config = getConfig()

    with TemporaryDirectory() as tmpdir:
        with Looper(debug=True) as looper:
            nodes = []
            for nm in NODEREG.keys():
                node = Node(nm, NODEREG, basedirpath=tmpdir)
                looper.add(node)
                node.startKeySharing()
                nodes.append(node)

            # load genesis transactions
            for node in nodes:
                node.addGenesisTxns(config.genesisTxns)

            looper.run()


if __name__ == "__main__":
    start()
