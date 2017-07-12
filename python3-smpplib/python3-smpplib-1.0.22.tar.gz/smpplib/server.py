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

    def __init__(self, init_seq=0x00000001):
        self._sequence = init_seq

    @property
    def sequence(self):
        return self._sequence

    def next_sequence(self):
        if self._sequence == self.MAX_SEQUENCE:
            self._sequence = self.MIN_SEQUENCE
        else:
            self._sequence += 1
        return self._sequence


class Esme(object):
    """Connected ESME client class"""

    def __init__(self, host, sock, server, sequence_generator=None):
        """Initialize"""

        self.vendor = None
        self.host = host
        self.custom_data = {}
        self._socket = sock
        self.uid = time.time()
        if sequence_generator is None:
            sequence_generator = SimpleSequenceGenerator()
        self.sequence_generator = sequence_generator
        self.state = consts.SMPP_CLIENT_STATE_OPEN
        self.server = server
        self.queue = Queue()
        queue_thread = threading.Thread(target=self.queue_processor)
        queue_thread.start()

    @property
    def sequence(self):
        return self.sequence_generator.sequence

    def next_sequence(self):
        return self.sequence_generator.next_sequence()

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
        """Send PDU to the ESME"""

        if self.state not in consts.COMMAND_STATES[p.command]:
            raise exceptions.PDUError(
                'Command {command} failed: {error}'.format(command=p.command,
                                                           error=consts.DESCRIPTIONS[consts.SMPP_ESME_RINVBNDSTS]))
        if p.command in consts.STATE_SETTERS:
            self.state = consts.STATE_SETTERS[p.command]

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
            while len(raw_len) < 4:
                raw_len += self._socket.recv(4 - len(raw_len))
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

        return p

    def _enquire_link_received(self, p):
        """Response to enquire_link"""

        ler = smpp.make_pdu('enquire_link_resp', client=self)
        ler.sequence = p.sequence
        self.send_pdu(ler)
        logging.debug('Link enquiry...')

    def submit_sm_handler(self, pdu):
        """Handle new message"""

        message_id = self.server.new_sms_handler(pdu=pdu, client=self)

        if message_id:
            answer_pdu = smpp.make_pdu('submit_sm_resp', client=self, message_id=message_id)
        else:
            answer_pdu = smpp.make_pdu('submit_sm_resp', client=self)
            answer_pdu.status = consts.SMPP_ESME_RSUBMITFAIL

        answer_pdu.sequence = pdu.sequence
        self.send_pdu(answer_pdu)

    def bind_handler(self, p):
        """Handle new binding"""

        answer_pdu = smpp.make_pdu(p.command + '_resp', client=self, system_id=p.system_id.decode('utf-8'))

        if self.server.authorization_handler(pdu=p, client=self):
            self.send_pdu(answer_pdu)
            return True
        else:
            answer_pdu.status = consts.SMPP_ESME_RINVPASWD
            self.send_pdu(answer_pdu)
            return False

    def _request_handler(self, p):
        """Handle all requests"""

        if p.command == 'unbind':
            logging.info('Unbind command received')
            resp = smpp.make_pdu('unbind_resp', client=self)
            self.send_pdu(resp)
        elif p.command == 'unbind_resp':
            self.state = consts.SMPP_CLIENT_STATE_CLOSED
            try:
                self._socket.close()
            except:
                pass
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
        elif p.command == 'submit_sm':
            self.submit_sm_handler(p)
        elif p.command == 'data_sm':
            answer_pdu = smpp.make_pdu(p.command + '_resp', client=self)
            self.send_pdu(answer_pdu)
        elif p.command == 'data_sm_resp':
            pass
        elif p.command == 'deliver_sm_resp':
            pass
        elif p.command == 'query_sm':
            pass
        elif p.command == 'cancel_sm':
            pass
        elif p.command == 'replace_sm':
            pass
        elif p.command == 'generic_nack':
            logging.warning('Wrong header! Received {command}'.format(command=p.command))
        else:
            logging.warning('Unhandled SMPP command {command}'.format(command=p.command))

    def deliver_handler(self, sms_id, phone, status, submit_date, done_date=None):
        """Send deliver_sm to ESME if registered_delivery is true"""

        message = 'id: ' + sms_id + ' sub:001 submit date:' + submit_date
        if status in ['DELIVRD', 'EXPIRED', 'UNDELIV', 'REJECTD', 'UNKNOWN'] and done_date is not None:
            message += ' done date:' + done_date
        message += ' stat:' + status
        message += ' err:000'
        answer_pdu = smpp.make_pdu('deliver_sm',
                                   client=self,
                                   short_message=message,
                                   destination_addr=phone,
                                   esm_class=consts.SMPP_MSGMODE_STOREDELIVERY,
                                   data_coding=consts.SMPP_ENCODING_DEFAULT,
                                   dest_addr_ton=consts.SMPP_TON_INTL,
                                   dest_addr_npi=consts.SMPP_NPI_ISDN,
                                   source_addr_ton=consts.SMPP_TON_INTL,
                                   source_addr_npi=consts.SMPP_NPI_ISDN,
                                   receipted_message_id=sms_id,
                                   message_state=consts.MESSAGE_STATES[status],
                                   network_error_code=b'\x03\x00\x00',
                                   service_type=None)
        self.send_pdu(answer_pdu)

    def queue_processor(self):
        """Queue processor for request PDU"""

        while self.state != consts.SMPP_CLIENT_STATE_CLOSED:
            try:
                p = self.queue.get(timeout=1)

                logging.debug('Get new task from queue: {command} ({uid})'.format(command=p.command,
                                                                                  uid=self.uid))
                self._request_handler(p)

                logging.debug('Finished processing task from queue: {command} ({uid})'.format(command=p.command,
                                                                                              uid=self.uid))
                self.queue.task_done()
            except Empty:
                pass

    def listen(self, ignore_error_codes=None):
        """Listen for PDUs and act"""

        while self.state != consts.SMPP_CLIENT_STATE_CLOSED:
            try:
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
                                                                   error=consts.DESCRIPTIONS.get(p.status, 'unknown')),
                            int(p.status))

                    if p.command in ['bind_transmitter', 'bind_receiver', 'bind_transceiver']:
                        if not self.bind_handler(p):
                            self.state = consts.SMPP_CLIENT_STATE_CLOSED
                            try:
                                self._socket.close()
                            except:
                                pass
                            try:
                                self._socket.shutdown(socket.SHUT_RDWR)
                            except:
                                pass
                    elif p.command == 'enquire_link':
                        self._enquire_link_received(p)
                    elif p.command == 'enquire_link_resp':
                        pass
                    else:
                        self.queue.put(p)

                except exceptions.PDUError as e:
                    if ignore_error_codes and len(e.args) > 1 and e.args[1] in ignore_error_codes:
                        logging.warning('({0}) {1}. Ignored.'.format(e.args[1], e.args[0]))
                    else:
                        raise
                except exceptions.ConnectionError as error:
                    logging.error('Connection error! Client: {uid}. Error: {error}'.format(uid=self.uid,
                                                                                           error=error))
                    self.state = consts.SMPP_CLIENT_STATE_CLOSED
            except Exception as error:
                logging.error('Unknown error: {error}'.format(error=error))
                try:
                    self.unbind()
                except Exception as error:
                    pass
                self.state = consts.SMPP_CLIENT_STATE_CLOSED

        if self in self.server.clients:
            self.server.clients.remove(self)


class Server(object):
    """SMPP server class"""

    def __init__(self, port=2775, max_connections=100):
        """Initialize"""

        self.port = int(port)
        self.max_connections = int(max_connections)
        self._clients_cs = threading.Lock()
        self.state = consts.SMPP_SERVER_STATE_CLOSED
        self.system_id = 'P1sms'
        self.clients = []

        err = True
        while err:
            err = False
            try:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.bind(('', self.port))
            except Exception as error:
                err = True
                logging.error('Socket Bind Error {error}'.format(error=error))
                if self._socket is not None:
                    try:
                        self._socket.close()
                    except:
                        pass
                    try:
                        self._socket.shutdown(socket.SHUT_RDWR)
                    except:
                        pass
                time.sleep(2)

    def up(self):
        """Start listening"""

        logging.info('Start listening at {port}...'.format(port=self.port))

        try:
            if self._socket is None:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.listen(self.max_connections)
            self.state = consts.SMPP_SERVER_STATE_OPEN

            server_thread = threading.Thread(target=self.accept)
            server_thread.daemon = True
            server_thread.start()
        except socket.error:
            raise exceptions.ConnectionError('Start listen error')

    def accept(self):
        """Accepting new clients"""

        while self.state == consts.SMPP_SERVER_STATE_OPEN:
            try:
                connection, address = self._socket.accept()
                self.new_esme(address[0], connection)
            except Exception as error:
                logging.error('SocketConnectError {error}'.format(error=error))

    def down(self):
        """Stop listening"""

        logging.info('Disconnecting...')

        for client in self.clients:
            if client.socket is not None:
                try:
                    client.unbind()
                except (exceptions.PDUError, exceptions.ConnectionError) as e:
                    if len(getattr(e, 'args', tuple())) > 1:
                        logging.warning('({0}) {1}. Ignored'.format(e.args[1], e.args[0]))
                    else:
                        logging.warning('{0}. Ignored'.format(e))

        if self._socket is not None:
            try:
                self._socket.close()
            except:
                pass
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
        self.state = consts.SMPP_SERVER_STATE_CLOSED

    def new_esme(self, esme_host, esme_sock):
        """Start new ESME listening"""

        try:
            client = Esme(esme_host, esme_sock, self)
            self.clients.append(client)

            esme_thread = threading.Thread(target=client.listen)
            esme_thread.daemon = True
            esme_thread.start()
        except Exception as error:
            logging.error('New client error: {error}'.format(error=error))

    @staticmethod
    def new_sms_handler(pdu, client, **kwargs):
        """Called when ESME send new sms.
        May be overridden"""
        logging.warning('New sms handler (Override me)')
        return False

    @staticmethod
    def authorization_handler(pdu, client, **kwargs):
        """Called when ESME bind to SMSC with credentials.
        May be overridden"""
        logging.warning('Authorization handler (Override me)')
        return False

    def set_new_sms_handler(self, func):
        """Set new function to handle new sms event"""
        self.new_sms_handler = func

    def set_authorization_handler(self, func):
        """Set new function to handle authorization event"""
        self.authorization_handler = func
