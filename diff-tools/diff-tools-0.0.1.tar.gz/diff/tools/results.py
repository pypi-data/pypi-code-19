import os
import json
from datetime import datetime

import pandas as pd
from tabulate import tabulate

from jinja2 import Template

from . import TEMPLATE_DIR


def summary_to_markdown(result, template_file='differences_template.rst'):
    template = open(os.path.join(TEMPLATE_DIR, template_file)).read()
    template = Template(template)
    data_diff = [d for d in result['differences'] if d['type'] == 'data_mismatch']
    data_diff = pd.DataFrame(data_diff)
    data_diff = tabulate(data_diff, data_diff.columns, tablefmt="pipe", showindex=False)
    return template.render(data=result, data_diff=data_diff)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


def summary_to_json(result):
    return json.dumps(result, cls=DateTimeEncoder)


def summary_to_df(result):
    diffs = result['differences']
    df = pd.DataFrame(filter(lambda row: True if row['type'] == 'data_mismatch' else False, diffs),
                      columns=['keys', 'columns', 'base_value', 'reg_value', 'type'])
    return df
