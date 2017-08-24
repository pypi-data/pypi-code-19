
import json

version_json = '''
{"version": "0.5.3rc2", "dirty": false, "full-revisionid": "5bd5ccb111c4a587df94cce720a666dc98e1b049", "error": null, "date": "2017-08-24T10:02:42.919587"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

