
import json

version_json = '''
{"version": "0.5.3", "date": "2017-08-24T10:47:49.269227", "error": null, "full-revisionid": "5bd5ccb111c4a587df94cce720a666dc98e1b049", "dirty": false}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

