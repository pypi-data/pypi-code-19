import os
import json

from diff.tools.results import summary_to_markdown

from . import TEST_DATA_DIR


def test_generate_results():
    result_file = os.path.join(TEST_DATA_DIR, 'result_example.json')
    results = open(result_file).read()
    results = json.loads(results)
    print summary_to_markdown(results)
