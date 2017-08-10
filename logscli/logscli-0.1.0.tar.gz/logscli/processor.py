import os
import gzip
import json
import re

class LogsProcessor:
    def __init__(self, logs_path):
        self.logs_path = os.path.abspath(logs_path)

    def process(self, file_path):
        file = gzip.open(file_path, 'r')

        with file as logs_file:
            for line in logs_file:
                data = self.lower_keys(json.loads(line))

                data["message"] = self.decode(data["message"])

                while 'message' in data['message']:
                    data['message'] = self.decode(data['message']['message'])

                # if 'transaction' in data['message']:
                #     data['message'] = data['message']['request']

                data["message"].pop('traceback', None)

                if 'http_request' in data["message"]:
                    if 'headers' in data["message"]["http_request"]:
                        data["message"]["http_request"]["headers"] = json.loads(data["message"]["http_request"]["headers"])
                    elif 'all' in data["message"]["http_request"]:
                        data["message"]["http_request"]['all'] = json.loads(data["message"]["http_request"]['all'])

                if 'ml_waf' in data['message']:
                    if data['message']['ml_waf']:
                        data['message']['ml_waf'] = json.loads(data['message']['ml_waf'])

                yield data['message']

    def logs(self):
        for file in os.listdir(self.logs_path):
            if file.endswith('.gz'):
                yield os.path.join(self.logs_path, file)

    def lower_keys(self, x):
        if isinstance(x, list):
            return [self.lower_keys(v) for v in x]
        elif isinstance(x, dict):
            return dict((k.lower(), self.lower_keys(v)) for k, v in x.items())
        else:
            return x

    def decode(self, encoded_string):
        try:
            encoded_string = json.loads(encoded_string)
        except json.decoder.JSONDecodeError:
            encoded_string = re.sub(r'\\x([a-fA-F0-9]{2})', r'\\u00\1', encoded_string)
            encoded_string = json.loads(encoded_string)

        return self.lower_keys(encoded_string)
