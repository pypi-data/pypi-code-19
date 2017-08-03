import logging

from twisted.internet import reactor, protocol
from twisted.internet.defer import succeed
from twisted.web._newclient import ResponseDone
from twisted.web.client import Agent
from twisted.web.iweb import IBodyProducer, UNKNOWN_LENGTH
from twisted.web.server import NOT_DONE_YET
from zope.interface import implementer

from txhttputil.site.BasicResource import BasicResource
from txhttputil.site.SpooledNamedTemporaryFile import SpooledNamedTemporaryFile
from txhttputil.util.DeferUtil import vortexLogFailure

logger = logging.getLogger(__name__)


@implementer(IBodyProducer)
class BytesProducer(object):
    def __init__(self, content: SpooledNamedTemporaryFile):
        self.content = content
        self.length = UNKNOWN_LENGTH

    def startProducing(self, consumer):
        # TODO, Properly implement Producer
        self.content.seek(0)
        consumer.write(self.content.read())
        return succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass


class _ResponseDataRelay(protocol.Protocol):
    def __init__(self, request):
        self._request = request

    def dataReceived(self, data):
        self._request.write(data)

    def connectionLost(self, reason):
        if not reason.check(ResponseDone):
            self._request.response_code = 500
            vortexLogFailure(reason, logger)
        self._request.finish()


class HttpResourceProxy(BasicResource):
    isGzipped = True
    isLeaf = True

    def __init__(self, serverIp: str, serverPort: int):
        """ Constructor

        @param serverIp: The IP or host name of the peek server to download from.
        @param serverPort: The port of the peek servers platform http site.
                            Not the admin site.
        """

        self._serverIp = serverIp
        self._serverPort = serverPort

    def render(self, request):
        # Construct an Agent.
        agent = Agent(reactor)

        url = "http://%s:%s%s" % (self._serverIp, self._serverPort, request.path.decode())

        headers = request.requestHeaders.copy()
        headers.removeHeader(b'host')  # The agent will reset these.

        d = agent.request(request.method,
                          url.encode(),
                          headers,
                          BytesProducer(request.content))

        def good(response):
            request.responseHeaders.setRawHeaders(
                b'content-type',response.headers.getRawHeaders(b'content-type')
            )
            request.response_code = response.code
            response.deliverBody(_ResponseDataRelay(request))

        def bad(failure):
            vortexLogFailure(failure, logger)
            request.response_code = 500
            request.write(str(failure.value).encode())
            request.finish()

        d.addCallbacks(good, bad)

        def closedError(failure):
            logger.error("Got closedError %s" % failure)

        request.notifyFinish().addErrback(closedError)

        return NOT_DONE_YET
