
import json

version_json = '''
{"version": "0.5.3rc1", "date": "2017-08-21T22:23:14.891486", "error": null, "dirty": false, "full-revisionid": "cea330ebdca015dc4aa64709f59b50683a4a3733"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

