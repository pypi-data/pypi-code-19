import json


class Config():
    def __init__(self):
        self.watch_directory = '/var/log/'
        self.ingest_endpoint = 'https://ingest.log.fit/log'

    def read_config_file(self, path):
        try:
            with open(path, 'r') as handle:
                data = handle.read()
        except IOError:
            return
        data = json.loads(data)
        self.parse_config_data(data)

    def parse_config_data(self, data):
        self.watch_directory = data.get(
            'watch_directory',
            self.watch_directory,
        )
        self.ingest_endpoint = data.get(
            'ingest_endpoint',
            self.ingest_endpoint,
        )
