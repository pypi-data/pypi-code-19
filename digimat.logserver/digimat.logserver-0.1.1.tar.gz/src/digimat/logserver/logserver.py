import pickle
import logging
import logging.handlers
import SocketServer
import struct
import argparse

import colorer


class LogFilterText(logging.Filter):
    def setString(self, text):
        self._filterText=text.lower()

    def filter(self, record):
        try:
            if self._filterText in record.getMessage().lower():
                return 1
            if self._filterText in record.name.lower():
                return 1
            return 0
        except:
            pass

        return 1


class LogRecordStreamHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """

        while True:
            try:
                chunk = self.connection.recv(4)
            except:
                break

            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.unPickle(chunk)
            record = logging.makeLogRecord(obj)
            self.handleLogRecord(record)

    def unPickle(self, data):
        return pickle.loads(data)

    def handleLogRecord(self, record):
        # if a name is specified, we use the named logger rather than the one
        # implied by the record.
        if self.server.logname is not None:
            name = self.server.logname
        else:
            name = record.name

        logger = logging.getLogger(name)
        # N.B. EVERY record gets logged. This is because Logger.handle
        # is normally called AFTER logger-level filtering. If you want
        # to do filtering, do it at the client end to save wasting
        # cycles and network bandwidth!

        try:
            f=self.server.textFilter.lower()
            if f in record.getMessage().lower() or f in record.name.lower():
                logger.handle(record)
            return
        except:
            pass

        logger.handle(record)


class LogRecordSocketReceiver(SocketServer.ThreadingTCPServer):
    """
    Simple TCP socket-based logging receiver suitable for testing.
    """

    allow_reuse_address = 1
    daemon_threads = True

    def __init__(self, host='', port=logging.handlers.DEFAULT_TCP_LOGGING_PORT, handler=LogRecordStreamHandler):
        SocketServer.ThreadingTCPServer.__init__(self, (host, port), handler)
        # self.allow_reuse_address=1
        # self.daemon_threads=True
        self.logname=None
        self.textFilter=None


def main():
    parser=argparse.ArgumentParser(description='digimat socket logserver')
    parser.add_argument('--filter', help='text filter')

    args=parser.parse_args()
    logging.basicConfig(
        # format='%(asctime)-15s %(name)-32s %(levelname)-8s %(message)s',
        format='%(asctime)-15s %(name)-32s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    tcpserver = LogRecordSocketReceiver()
    tcpserver.textFilter=args.filter
    # tcpserver.daemon_threads=True
    # tcpserver.allow_reuse_address=1

    print 'Starting TCP Logging Server'
    if args.filter:
        print "Filtering active [%s]" % args.filter
    print 'Listening...'
    try:
        tcpserver.serve_forever()
    except:
        pass

    print "Shutdown..."
    tcpserver.shutdown()
    tcpserver.server_close()

    print('Done.')


if __name__ == '__main__':
    main()
