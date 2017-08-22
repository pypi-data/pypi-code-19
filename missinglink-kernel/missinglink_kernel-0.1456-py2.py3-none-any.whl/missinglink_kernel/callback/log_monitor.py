# coding=utf-8
import json
import os
import socket
import logging
import argparse
from errno import EAGAIN
import requests
import asyncore
import struct
import time


# noinspection PyClassicStyleClass
class DataHandler:
    def __init__(self, endpoint):
        self.pending_data = None
        self.endpoint = endpoint
        self.session = requests.session() if endpoint is not None else None
        self.data_callback = None

    def post_json(self, data):
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        self.session.post(self.endpoint, data=json.dumps(data), headers=headers)

    def on_line(self, line, is_json):
        if is_json:
            try:
                data = json.loads(line)
            except ValueError:
                return
        else:
            data = {
                'text': line,
            }

        if self.session is not None:
            self.post_json(data)
        elif self.data_callback is not None:
            self.data_callback(data)

    def process_text(self, text, is_json):
        if len(text) == 0:
            return

        lines = text.split('\n')

        for i, line in enumerate(lines):
            if self.pending_data is not None:
                line = self.pending_data + line
                self.pending_data = None

            if i == len(lines) - 1:  # last or first (and only one)
                if len(line) == 0 or text[-1] != '\n':
                    self.pending_data = line
                    continue

            self.on_line(line, is_json)


# noinspection PyClassicStyleClass
class IncomingDataHandler(asyncore.dispatcher):
    def __init__(self, port, endpoint, data_handler=None):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(('', port))
        self.data_handler = data_handler or DataHandler(endpoint)
        self.is_closed = False

    def writable(self):
        return False

    def read_at_least(self, data, size, wait_for_data):
        while len(data) < size:
            try:
                current_data = self.recv(size)
                data += current_data
            except socket.error as why:
                if why.errno == EAGAIN:
                    if wait_for_data:
                        time.sleep(0.1)
                        continue
                    else:
                        return data

                raise

            if len(data) == 0:
                return

        return data

    def handle_read(self):
        total_read = 0
        data = b''
        while True:
            data = self.read_at_least(data, 4, wait_for_data=False)
            if not data:
                break

            size = struct.unpack('!i', data[:4])[0]

            if size == 0:  # the application sent zero size in order to close this
                self.close()
                break

            data = data[4:]

            data = self.read_at_least(data, size, wait_for_data=True)

            current_block = data[:size].decode('utf8')
            data = data[size:]

            total_read += 4 + size

            self.data_handler.process_text(current_block, is_json=True)

        return total_read

    def handle_close(self):
        self.is_closed = True
        self.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='listen socket for logs.')
    parser.add_argument('--port', type=int)
    parser.add_argument('--endpoint')
    parser.add_argument('--reportEndpoint')

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    logging.info('log monitor started on pid %s', os.getpid())

    handler = None
    if args.port is not None:
        handler = IncomingDataHandler(args.port, args.endpoint)
        asyncore.loop()

        if args.reportEndpoint:
            requests.post(args.reportEndpoint)
