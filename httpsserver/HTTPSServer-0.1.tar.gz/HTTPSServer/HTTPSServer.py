import BaseHTTPServer
import sys
import ssl

class HTTPSServer(BaseHTTPServer.HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, certfile, bind_and_activate=True,
        keyfile=None, cert_reqs=0, ssl_version=2, ca_certs=None, do_handshake_on_connect=True, suppress_ragged_eofs=True, ciphers=None):
        
        BaseHTTPServer.HTTPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        self.socket = ssl.wrap_socket(self.socket, keyfile, certfile, True, cert_reqs, ssl_version, ca_certs, do_handshake_on_connect, suppress_ragged_eofs, ciphers)



def test(HandlerClass = BaseHTTPServer.BaseHTTPRequestHandler,
         ServerClass = HTTPSServer, protocol="HTTP/1.0"):
    """Test the HTTP request handler class.

    This runs an HTTPS server on port 4443 (or the first command line
    argument).

    """

    if sys.argv[1:]:
        certfile = sys.argv[1]
    else:
        certfile = None

    if sys.argv[2:]:
        port = int(sys.argv[2])
    else:
        port = 4443
    server_address = ('', port)

    HandlerClass.protocol_version = protocol
    httpd = ServerClass(server_address, HandlerClass, certfile)

    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."
    httpd.serve_forever()


if __name__ == '__main__':
    test()

