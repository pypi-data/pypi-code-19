
import json

version_json = '''
{"dirty": false, "full-revisionid": "5bd5ccb111c4a587df94cce720a666dc98e1b049", "version": "0.5.3rc2", "date": "2017-08-24T10:09:07.139005", "error": null}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

