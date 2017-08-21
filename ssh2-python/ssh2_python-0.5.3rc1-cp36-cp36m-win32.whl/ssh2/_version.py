
import json

version_json = '''
{"date": "2017-08-21T22:30:15.620328", "dirty": false, "error": null, "full-revisionid": "cea330ebdca015dc4aa64709f59b50683a4a3733", "version": "0.5.3rc1"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

