import socket
from autest.api import AddWhenFunction
import hosts.output as host

def PortOpen(port, address=None):

    ret = False
    if address is None:
        address = "localhost"

    address = (address, port)

    try:
        s = socket.create_connection(address, timeout=.5)
        s.close()
        ret = True
    except socket.error:
        s = None
        ret = False
    except socket.timeout:
        s = None
    host.WriteDebug(["portopen", "when"],
                    "checking port {0} = {1}".format(port, ret))

    return ret


AddWhenFunction(PortOpen)
