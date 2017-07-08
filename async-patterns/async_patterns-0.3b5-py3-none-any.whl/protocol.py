import asyncio
import concurrent.futures
import logging
import pickle
import io

logger = logging.getLogger(__name__)

class Protocol(asyncio.Protocol):
    def __init__(self, loop):
        logger.debug('Protocol created')
        self.loop = loop
        self.__message_id_last = 0
        self.__message_futures = {}
        self.queue_packet_acall = asyncio.Queue()
        
    def __next_message_id(self):
        self.__message_id_last += 1
        return self.__message_id_last

    def connection_made(self, transport):
        logger.debug('Connection made')
        logger.debug('transport = {}'.format(transport))
        peername = transport.get_extra_info('peername')
        logger.debug('Connection from {}'.format(peername))
        self.transport = transport
     
    def connection_lost(self, exc):
        logger.debug('The server closed the connection {}'.format(exc))
    
    def data_received(self, data):
        logger.debug('Received {} bytes'.format(len(data)))
        
        l = len(data)

        stream = io.BytesIO(data)
            
        while stream.tell() < l:
            logger.debug('{} bytes in stream. at position {}.'.format(len(stream.getbuffer()), stream.tell()))
            packet = pickle.load(stream)
            self.__packet_received(packet)
    
    async def async_packet_received(self, packet):
        try:
            res = await packet(self)
        except concurrent.futures.CancelledError as e:
            logger.exception('packet call cancelled. packet={} {}'.format(repr(packet), e))
        except Exception as e:
            logger.exception('error during packet call. {}'.format(e))
        else:
            logger.info('packet call returned {}'.format(repr(res)))

    def __packet_received(self, packet):
        logger.debug('packet received: {}'.format(repr(packet)))

        task = self.loop.create_task(self.async_packet_received(packet))

        # keep track of packet acall coroutines
        packet._task_acall = task
        self.queue_packet_acall.put_nowait(task)

        if hasattr(packet, 'response_to'):
            future = self.__message_futures[packet.response_to]
            future.set_result(packet)

        return task

    def write(self, packet):
        """
        Write an object to the socket.
        Assign the object a ``message_id`` before sending.

        :param packet: object to pickle and send
        :rtype: future
        """
        packet.message_id = self.__next_message_id()
        b = pickle.dumps(packet)
        self.transport.write(b)
        
        logger.debug('write {} {} bytes'.format(packet.__class__.__name__, len(b)))

        fut = self.loop.create_future()
        self.__message_futures[packet.message_id] = fut
        return fut

    async def close(self):
        """
        This method is a :ref:`coroutine <coroutine>`.
        """
        logger.debug('cancel packet acall')
        while not self.queue_packet_acall.empty():
            task = self.queue_packet_acall.get_nowait()

            logger.debug('  task = {}'.format(repr(task)))

            task.cancel()



