import ntpath
import re
import os
import json
import csv
import sys

class LogsFormatter:
    def __init__(self, output_path, format, config):
        self.output_path = output_path
        self.format = format
        self.config = config

    def run(self, logs_processor):
        matcher = re.compile("_[0-9]{8}-[0-9]{4,5}[PM|AM]+-(.*).log.gz")

        for log_file in logs_processor.logs():
            file_name = ntpath.basename(log_file)

            try:
                logs_type = matcher.search(file_name).groups()[0]
            except AttributeError:
                print('ERROR: when loading ' + file_name)
                continue


            file_name = os.path.splitext(file_name)[0]
            output = os.path.join(self.output_path, file_name + '.' + self.format)

            if os.path.exists(output):
                print('INFO: skipping ' + output + ' already processed')
                continue

            if self.format == 'json':
                self.process_json(logs_processor.process(log_file), output)

            if self.format == 'csv':
                self.process_csv(logs_processor.process(log_file), output, logs_type)

    def process_json(self, logs, output_path):
        print('INFO: writing ' + output_path)
        output = open(output_path, 'w')
        for log in logs:
            output.write(json.dumps(log) + '\n')
        output.close

    def process_csv(self, logs, output_path, logs_type):
        try:
            output_keys = self.config['output'][logs_type]
        except:
            print('ERROR: missing output definition for "' + logs_type + '" possible keys: ')
            print(next(logs).keys())
            sys.exit(1)

        print('INFO: writing ' + output_path)
        output = open(output_path, 'w')
        writer = csv.DictWriter(output, fieldnames=output_keys)
        writer.writeheader()
        for log in logs:
            filtered_log = { key:value for key, value in log.items() if key in output_keys }
            writer.writerow(filtered_log)
