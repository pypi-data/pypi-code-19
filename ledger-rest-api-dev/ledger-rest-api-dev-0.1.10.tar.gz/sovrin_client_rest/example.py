from tempfile import TemporaryDirectory

from stp_core.loop.looper import Looper
from sovrin_node.server.node import Node

from sovrin_client_rest.persistent_client import PersistentClient

with TemporaryDirectory() as tmpdir:
    with Looper(debug=True) as looper:
        nodeReg = {
            'Alpha': ('127.0.0.1', 7560),
            'Beta': ('127.0.0.1', 7562),
            'Gamma': ('127.0.0.1', 7564),
            'Delta': ('127.0.0.1', 7566)
        }
        nodes = []
        for nm in nodeReg.keys():
            node = Node(nm, nodeReg, basedirpath=tmpdir)
            looper.add(node)
            node.startKeySharing()
            nodes.append(node)

        looper.runFor(5)

        cliNodeReg = {
            'AlphaC': ('127.0.0.1', 7561),
            'BetaC': ('127.0.0.1', 7563),
            'GammaC': ('127.0.0.1', 7565),
            'DeltaC': ('127.0.0.1', 7567)}
        client_addr = ("127.0.0.1", 8000)
        clientName = "client1"
        client = PersistentClient(clientName=clientName,
                                  ha=client_addr,
                                  nodeReg=cliNodeReg,
                                  basedirpath=tmpdir)
        looper.add(client)

        idAndKey = client.signer.identifier, client.signer.verkey
        for node in nodes:
            node.clientAuthNr.addClient(*idAndKey)
        looper.runFor(3)

        msg = {'life_answer': 42}
        request, = client.submit(msg)

        looper.runFor(5)

        reply, status = client.getReply(request.reqId)

        print("Reply: {}\n".format(reply))
        print("Status: {}\n".format(status))