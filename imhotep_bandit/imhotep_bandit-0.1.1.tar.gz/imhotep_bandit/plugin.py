import json
import textwrap
from collections import defaultdict

from imhotep.tools import Tool


class Bandit(Tool):
    file_extensions = ['py']

    def invoke(self, dirname, filenames, linter_configs):
        retval = defaultdict(lambda: defaultdict(list))

        filenames = [
            x for x in filenames
            if x.split('.')[-1] in self.file_extensions
        ]

        if filenames:
            files = ' '.join(filenames)
        else:
            files = '-r %s' % dirname

        if linter_configs:
            linter_config_option = '--ini %s' % linter_configs.pop()
        else:
            linter_config_option = ''

        cmd = 'bandit -f json %s %s' % (files, linter_config_option)
        output = self.executor(cmd)
        data = json.loads(output.decode('utf8'))

        for result in data['results']:
            line = str(result['line_number'])
            message = self.format_message(result)
            retval[result['filename']][line].append(message)

        return self.to_dict(retval)

    def format_message(self, report):
        return textwrap.dedent("""
            **{test_id}**: {issue_text}
            Severity: {issue_severity}, Confidence: {issue_confidence}
        """.format(**report)).strip()

    def to_dict(self, d):
        if not isinstance(d, dict):
            return d

        return {
            k: self.to_dict(v) for k, v in d.items()
        }

    def get_configs(self):
        return ['**/.bandit']
