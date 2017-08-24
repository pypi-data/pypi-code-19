
import json

version_json = '''
{"full-revisionid": "5bd5ccb111c4a587df94cce720a666dc98e1b049", "version": "0.5.3rc2", "date": "2017-08-24T09:59:38.517190", "error": null, "dirty": false}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

