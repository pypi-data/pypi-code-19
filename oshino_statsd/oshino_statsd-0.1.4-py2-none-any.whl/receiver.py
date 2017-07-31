import socketserver
import queue
import logbook


class UdpHandler(socketserver.BaseRequestHandler):

    def __init__(self, *args, queue):
        self.q = queue
        self.logger = logbook.Logger("UDP Handler")
        super(UdpHandler, self).__init__(*args)

    def _add_to_queue(self, data):
        try:
            self.q.put(data)
        except queue.Full:
            self.logger.warning("Queue is full.")
            self.q.get()
            self.logger.warning("Removing last item and retrying")
            self._add_to_queue(data)

    def handle(self):
        data, _ = self.request
        self._add_to_queue(data)


def run(host, port, q, logger):

    def bind_fn(request, addr, sock):
        return UdpHandler(request, addr, sock, queue=q)

    server = socketserver.UDPServer((host, port), bind_fn)
    logger.info("Starting UDP server on {0}:{1}".format(host, port))
    server.serve_forever()
