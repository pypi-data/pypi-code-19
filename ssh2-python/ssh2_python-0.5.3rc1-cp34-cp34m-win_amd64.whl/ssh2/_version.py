
import json

version_json = '''
{"error": null, "dirty": false, "date": "2017-08-21T22:19:56.589935", "version": "0.5.3rc1", "full-revisionid": "cea330ebdca015dc4aa64709f59b50683a4a3733"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

