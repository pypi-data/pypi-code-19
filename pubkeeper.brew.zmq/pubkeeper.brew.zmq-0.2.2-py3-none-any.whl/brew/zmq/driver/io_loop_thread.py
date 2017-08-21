"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from threading import Thread, Event
from zmq.eventloop import zmqstream

from pubkeeper.utils.logging import get_logger


class ZMQIoLoopThread(Thread):

    """ This class host an io_loop within a thread. An io_loop is an I/O
    event loop for non-blocking sockets.

    Currently it provides functionality that is equivalent to io_loop_thread
    in a simplified fashion.
    """

    def __init__(self, io_loop, subscriber, handler):
        """ Initializes the thread.
        """
        super(ZMQIoLoopThread, self).__init__(daemon=True)
        self.logger = get_logger(self.__class__.__name__)

        self._io_loop = io_loop
        self._subscriber = subscriber
        self._handler = handler
        self._stream = None
        self._stopped = False
        self._io_loop_stopped = Event()

    def run(self):
        self._stream = zmqstream.ZMQStream(self._subscriber, self._io_loop)
        self._stream.on_recv(self._message_handler)

        # Starts the loop, which  will run until "stop" is called.
        try:
            self._io_loop.start()
        except Exception:  # pragma: no cover (zmq generated exception)
            if not self._stopped:
                self.logger.exception("Exception caught on polling loop")
                self._close_loop()
                self._io_loop_stopped.set()
                raise
        self._close_loop()
        self._io_loop_stopped.set()

    def stop(self):
        """ Stops the thread by stopping the io_loop
        """
        # make sure thread is fully started.
        self._started.wait()

        self._stopped = True
        if self._stream and not self._stream.closed():
            self._stream.stop_on_recv()
            try:
                self._stream.flush()
                self._stream.close()
            except Exception:  # pragma: no cover
                self.logger.debug("Exception when flushing and closing",
                                  exc_info=True)
        self._stream = None
        # under heavy load, io_loop.stop has shown to throw exceptions
        try:
            self._io_loop.stop()
        except Exception:  # pragma: no cover
            # under heavy load, io_loop.stop has shown to throw exceptions
            # that have turned out to be irrelevant
            # mainly ignore exception when stopping, log to debug
            self.logger.debug("Exception when stopping io_loop",
                              exc_info=True)

        # wait for io_loop to be done
        self._io_loop_stopped.wait()
        self._io_loop_stopped.clear()

    def _message_handler(self, msgs):
        try:
            self._handler(self._get_msg_data(msgs))
        except Exception:
            self.logger.exception(
                "Exception caught on user function: '{0}'".
                format(self._handler.__name__))

    @staticmethod
    def _get_msg_data(msgs):
        """ Gets the actual message data

        Message contents depend on how they are sent, i.e. send,
        send_multipart, etc, therefore subscriber would know how to interpret
        message.

        This method deals with messages sent through send, therefore there
        is just one part in the list (the message itself)

        Override this method to accommodate other 'sending-ways'

        Args:
            msgs (list): msgs parts as delivered by stream

        Returns:
            msg data

        """
        return msgs[0]

    def _close_loop(self):
        try:
            self._io_loop.close()
        except Exception:  # pragma: no cover
            self.logger.warning("io_loop could not be closed")
