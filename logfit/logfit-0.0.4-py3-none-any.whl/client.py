import json
import logging
import os
import requests
from time import sleep

import magic

from logfit.daemon import Daemon
from logfit.tail import TailedFile


ALLOWED_MIME_TYPES = [
    'text/plain',
    'inode/x-empty',
]
INGEST_ENDPOINT = 'https://ingest.log.fit/log'
DEFAULT_DIRECTORY = '/var/log/'


class LogFit(Daemon):
    def __init__(self, *args, **kwargs):
        if 'directory' in kwargs:
            self.directory = kwargs.pop('directory')
        else:
            self.directory = DEFAULT_DIRECTORY
        self.tails = {}
        super().__init__(*args, **kwargs)

    def run(self):
        self.find_log_files()
        while True:
            sleep(5)
            self.read_logs()

    def stop(self, *args, **kwargs):
        for file_path, tail in self.tails.items():
            tail.close()
        if self.is_running():
            super().stop(*args, **kwargs)

    def read_logs(self):
        for path, tail in self.tails.items():
            while True:
                line = tail.readline()
                if not line:
                    break
                self.send_line(path, line)

    def find_log_files(self):
        for root, subdirs, file_names in os.walk(self.directory):
            for file_name in file_names:
                path = os.path.join(root, file_name)
                self.tail_file(path)

    def tail_file(self, file_path):
        try:
            open(file_path, 'r').close()
        except IOError as e:
            return
        mime_type = magic.from_file(file_path, mime=True)
        if mime_type not in ALLOWED_MIME_TYPES:
            return
        tail = TailedFile(file_path)
        self.tails[file_path] = tail
        self.log("Tailing " + file_path, logging.DEBUG)

    def send_line(self, path, line):
        data = {
            'row_data': line,
            'log_location': path,
        }
        data = json.dumps(data)
        requests.post(INGEST_ENDPOINT, data=data)
        self.log("Sending data from " + path, logging.DEBUG)
