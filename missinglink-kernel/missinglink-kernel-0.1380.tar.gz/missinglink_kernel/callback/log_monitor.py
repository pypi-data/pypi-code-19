# coding=utf-8
import json
import os
import socket
import logging
import argparse
import requests
import asyncore


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

    def handle_read(self):
        buffer_size = 8 * 1024
        total_read = 0
        while True:
            data = self.recv(buffer_size)

            data = data.decode('utf8')

            total_read += len(data)

            self.data_handler.process_text(data, is_json=True)

            if buffer_size > len(data):
                break

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
