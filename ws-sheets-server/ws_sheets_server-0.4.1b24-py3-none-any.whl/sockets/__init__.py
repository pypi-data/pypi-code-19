import os
import pickle
import numpy
import traceback
import logging

import mysocket
import sheets_backend

logger = logging.getLogger(__name__)


class Client(mysocket.Client):
    def __init__(self, port):
        mysocket.Client.__init__(self, '', port)

    def recv_packet(self):
        b = self.recv()
        o = pickle.loads(b)
        if not isinstance(o, Packet):
            logger.error('bytes:',repr(b))
            raise TypeError()
        return o
    
    def book_new(self):
        self.send(pickle.dumps(RequestBookNew()))
        return self.recv_packet()
    
class BookProxy(sheets_backend.BookProxy, mysocket.Client):
    def __init__(self, book_id, port):
        mysocket.Client.__init__(self, '', port)
        self.book_id = book_id

    def recv_packet(self):
        o = pickle.loads(self.recv())
        if not isinstance(o, Packet): raise TypeError()
        return o

    def send_recv_packet(self, packet):
        self.send(pickle.dumps(packet))
        return self.recv_packet()

    def set_docs(self, s):
        return self.send_recv_packet(SetDocs(self.book_id, s))

    def set_cell(self, k, r, c, s):
        return self.send_recv_packet(SetCell(self.book_id, k, r, c, s))
    
    def set_script_pre(self, s):
        self.send(pickle.dumps(SetScriptPre(self.book_id, s)))
        return self.recv_packet()

    def set_script_post(self, s):
        self.send(pickle.dumps(SetScriptPost(self.book_id, s)))
        return self.recv_packet()

    def get_sheet_data(self, sheet_key):
        self.send(pickle.dumps(GetSheetData(self.book_id, sheet_key)))
        return self.recv_packet()

    def get_script_post_output(self):
        self.send(pickle.dumps(GetScriptPostOutput(self.book_id)))
        return self.recv_packet()
    
    def get_cell_data(self, sheet_key):
        self.send(pickle.dumps(GetCellData(self.book_id, sheet_key)))
        return self.recv_packet()

    def add_column(self, sheet_key, i):
        self.send(pickle.dumps(AddColumn(self.book_id, sheet_key, i)))
        return self.recv_packet()

    def add_row(self, sheet_key, i):
        self.send(pickle.dumps(AddRow(self.book_id, sheet_key, i)))
        return self.recv_packet()


