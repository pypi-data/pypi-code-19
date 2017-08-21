
import json

version_json = '''
{"full-revisionid": "cea330ebdca015dc4aa64709f59b50683a4a3733", "error": null, "date": "2017-08-21T22:26:36.089556", "dirty": false, "version": "0.5.3rc1"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

