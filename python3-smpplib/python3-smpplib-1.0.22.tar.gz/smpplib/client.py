import socket
import struct
import binascii
import logging
import time
import threading
from queue import Queue, Empty
from . import smpp
from . import exceptions
from . import consts


class SimpleSequenceGenerator(object):
    MIN_SEQUENCE = 0x00000001
    MAX_SEQUENCE = 0x7FFFFFFF

    def __init__(self):
        self._sequence = self.MIN_SEQUENCE

    @property
    def sequence(self):
        return self._sequence

    def next_sequence(self):
        if self._sequence == self.MAX_SEQUENCE:
            self._sequence = self.MIN_SEQUENCE
        else:
            self._sequence += 1
        return self._sequence


class Client(object):
    """SMPP client class"""

    def __init__(self, host, port, timeout=30, sequence_generator=None):
        """Initialize"""

        self.vendor = None
        self.host = host
        self.uid = time.time()
        self.port = int(port)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(timeout)
        self.receiver_mode = False
        if sequence_generator is None:
            sequence_generator = SimpleSequenceGenerator()
        self.sequence_generator = sequence_generator
        self.state = consts.SMPP_CLIENT_STATE_CLOSED
        self.queue = Queue()

    def __del__(self):
        """Disconnect when client object is destroyed"""

        if hasattr(self, '_socket') and self._socket is not None:
            try:
                self.unbind()
            except (exceptions.PDUError, exceptions.ConnectionError) as error:
                if len(getattr(error, 'args', tuple())) > 1:
                    logging.warning('({0}) {1}. Ignored'.format(error.args[1], error.args[0]))
                else:
                    logging.warning('{error}. Ignored'.format(error=error))
            self.disconnect()

    @property
    def sequence(self):
        return self.sequence_generator.sequence

    def next_sequence(self):
        return self.sequence_generator.next_sequence()

    def connect(self):
        """Connect to SMSC"""

        logging.info('Connecting to {host}:{port}...'.format(host=self.host, port=self.port))

        try:
            if self._socket is None:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect((self.host, self.port))
            self.state = consts.SMPP_CLIENT_STATE_OPEN

            queue_thread = threading.Thread(target=self.queue_processor)
            queue_thread.start()
        except socket.error:
            raise exceptions.ConnectionError("Connection refused")

    def disconnect(self):
        """Disconnect from the SMSC"""

        logging.info('Disconnecting...')

        if self._socket is not None:
            self._socket.close()
            self._socket = None
        self.state = consts.SMPP_CLIENT_STATE_CLOSED
        self.queue.join()

    def _bind(self, command_name, **kwargs):
        """Send bind_transmitter command to the SMSC"""

        if command_name in ('bind_receiver', 'bind_transceiver'):
            logging.debug('Receiver mode')
            self.receiver_mode = True

        p = smpp.make_pdu(command_name, client=self, **kwargs)
        self.send_pdu(p)

        try:
            resp = self.read_pdu()
        except socket.timeout:
            raise exceptions.ConnectionError()
        if resp.is_error():
            raise exceptions.PDUError(
                '({status}) {command}: {error}'.format(status=resp.status,
                                                       command=resp.command,
                                                       error=consts.DESCRIPTIONS.get(resp.status, 'unknown code')),
                int(resp.status))
        return resp

    def bind_transmitter(self, **kwargs):
        """Bind as a transmitter"""

        return self._bind('bind_transmitter', **kwargs)

    def bind_receiver(self, **kwargs):
        """Bind as a receiver"""

        return self._bind('bind_receiver', **kwargs)

    def bind_transceiver(self, **kwargs):
        """Bind as a transmitter and receiver at once"""

        return self._bind('bind_transceiver', **kwargs)

    def unbind(self):
        """Unbind from the SMSC"""

        logging.debug('Unbind client {uid}...'.format(uid=self.uid))
        p = smpp.make_pdu('unbind', client=self)
        self.send_pdu(p)

        try:
            return self.read_pdu()
        except socket.timeout:
            raise exceptions.ConnectionError()

    def send_pdu(self, p):
        """Send PDU to the SMSC"""

        if not self.state in consts.COMMAND_STATES[p.command]:
            raise exceptions.PDUError(
                'Command {command} failed: {error}'.format(command=p.command,
                                                           error=consts.DESCRIPTIONS[consts.SMPP_ESME_RINVBNDSTS]))
        logging.debug('Sending {command} PDU to {host} ({uid})'.format(command=p.command,
                                                                       host=self.host,
                                                                       uid=self.uid))
        generated = p.generate()

        logging.debug('>>{pdu} ({length} bytes) ({uid})'.format(pdu=binascii.b2a_hex(generated),
                                                                length=len(generated),
                                                                uid=self.uid))
        sent = 0

        while sent < len(generated):
            sent_last = 0
            try:
                sent_last = self._socket.send(generated[sent:])
            except socket.error as e:
                logging.warning(e)
                raise exceptions.ConnectionError()
            if sent_last == 0:
                raise exceptions.ConnectionError()
            sent += sent_last

        return True

    def read_pdu(self):
        """Read PDU from the ESME"""

        logging.debug('Waiting for PDU...')

        try:
            raw_len = self._socket.recv(4)
        except socket.timeout:
            raise
        except socket.error as e:
            logging.warning(e)
            raise exceptions.ConnectionError()
        if not raw_len:
            raise exceptions.ConnectionError()

        try:
            length = struct.unpack('>L', raw_len)[0]
        except struct.error:
            logging.warning('Receive broken pdu... {raw_len}'.format(raw_len=repr(raw_len)))
            raise exceptions.PDUError('Broken PDU')

        raw_pdu = raw_len
        while len(raw_pdu) < length:
            raw_pdu += self._socket.recv(length - len(raw_pdu))

        logging.debug('<<{pdu} ({length} bytes) ({uid})'.format(pdu=binascii.b2a_hex(raw_pdu),
                                                                length=len(raw_pdu),
                                                                uid=self.uid))
        p = smpp.parse_pdu(raw_pdu, client=self)

        logging.debug('Read {command} PDU from {host} ({uid})'.format(command=p.command,
                                                                      host=self.host,
                                                                      uid=self.uid))
        if p.is_error():
            return p
        elif p.command in consts.STATE_SETTERS:
            self.state = consts.STATE_SETTERS[p.command]

        return p

    def _message_received(self, p):
        """Handler for received message event"""

        dsmr = smpp.make_pdu('deliver_sm_resp', client=self)
        dsmr.sequence = p.sequence
        self.send_pdu(dsmr)
        self.message_received_handler(pdu=p)

    def _enquire_link_received(self):
        """Response to enquire_link"""

        ler = smpp.make_pdu('enquire_link_resp', client=self)
        self.send_pdu(ler)
        logging.debug('Link enquiry...')

    def set_message_received_handler(self, func):
        """Set new function to handle message receive event"""

        self.message_received_handler = func

    def set_message_sent_handler(self, func):
        """Set new function to handle message sent event"""

        self.message_sent_handler = func

    @staticmethod
    def message_received_handler(pdu, **kwargs):
        """Custom handler to process received message. May be overridden"""

        logging.warning('Message received handler (Override me)')

    @staticmethod
    def message_sent_handler(pdu, **kwargs):
        """Called when SMPP server accept message (SUBMIT_SM_RESP).
        May be overridden"""

        logging.warning('Message sent handler (Override me)')

    def _request_handler(self, p):
        """Handle all requests"""

        if p.command == 'unbind':
            logging.info('Unbind command received')
            resp = smpp.make_pdu('unbind_resp', client=self)
            self.send_pdu(resp)
        elif p.command == 'submit_sm_resp':
            self.message_sent_handler(p)
        elif p.command == 'deliver_sm':
            self._message_received(p)
        elif p.command == 'enquire_link':
            self._enquire_link_received()
        elif p.command == 'enquire_link_resp':
            pass
        else:
            logging.warning('Unhandled SMPP command {command}'.format(command=p.command))

    def queue_processor(self):
        """Queue processor for request PDU"""

        while self.state != consts.SMPP_CLIENT_STATE_CLOSED:
            try:
                p = self.queue.get(timeout=1)
                self._request_handler(p)
                self.queue.task_done()
            except Empty:
                pass

    def listen(self, ignore_error_codes=None):
        """Listen for PDUs and act"""

        while self.state != consts.SMPP_CLIENT_STATE_CLOSED:
            try:
                try:
                    p = self.read_pdu()
                except socket.timeout:
                    logging.debug('Socket timeout, listening again')
                    p = smpp.make_pdu('enquire_link', client=self)
                    self.send_pdu(p)
                    continue

                if p.is_error():
                    raise exceptions.PDUError(
                        '({status}) {command}: {error}'.format(status=p.status,
                                                               command=p.command,
                                                               error=consts.DESCRIPTIONS.get(p.status, 'unknown code')),
                        int(p.status))

                self.queue.put(p)

            except exceptions.PDUError as error:
                if ignore_error_codes and len(error.args) > 1 and error.args[1] in ignore_error_codes:
                    logging.warning('({0}) {1}. Ignored.'.format(error.args[1], error.args[0]))
                else:
                    raise

    def send_message(self, **kwargs):
        """Send message

        Required Arguments:
            source_addr_ton -- Source address TON
            source_addr -- Source address (string)
            dest_addr_ton -- Destination address TON
            destination_addr -- Destination address (string)
            short_message -- Message text (string)
        """

        ssm = smpp.make_pdu('submit_sm', client=self, **kwargs)
        self.send_pdu(ssm)

        return ssm
