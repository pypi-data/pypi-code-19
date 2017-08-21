
import json

version_json = '''
{"version": "0.5.3rc1", "full-revisionid": "cea330ebdca015dc4aa64709f59b50683a4a3733", "dirty": false, "date": "2017-08-21T22:17:03.974726", "error": null}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

