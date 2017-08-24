
import json

version_json = '''
{"date": "2017-08-24T10:20:41.751000", "full-revisionid": "5bd5ccb111c4a587df94cce720a666dc98e1b049", "dirty": false, "version": "0.5.3rc2", "error": null}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

