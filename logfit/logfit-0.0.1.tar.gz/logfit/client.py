import os
from time import sleep

from logfit.daemon import Daemon
from logfit.tail import TailedFile


class LogFit(Daemon):
    def __init__(self, *args, **kwargs):
        if 'directory' in kwargs:
            self.directory = kwargs.pop('directory')
        else:
            self.directory = "/var/log/"
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
                print(path, line, end='')

    def find_log_files(self):
        for root, subdirs, file_names in os.walk(self.directory):
            for file_name in file_names:
                path = os.path.join(root, file_name)
                self.tail_file(path)

    def tail_file(self, file_path):
        tail = TailedFile(file_path)
        self.tails[file_path] = tail
