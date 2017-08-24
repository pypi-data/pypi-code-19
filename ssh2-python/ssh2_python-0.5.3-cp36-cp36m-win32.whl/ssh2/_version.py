
import json

version_json = '''
{"date": "2017-08-24T10:57:46.015217", "dirty": false, "error": null, "full-revisionid": "5bd5ccb111c4a587df94cce720a666dc98e1b049", "version": "0.5.3"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

