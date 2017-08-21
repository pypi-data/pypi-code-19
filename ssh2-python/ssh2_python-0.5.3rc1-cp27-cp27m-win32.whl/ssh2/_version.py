
import json

version_json = '''
{"date": "2017-08-21T22:36:48.408000", "full-revisionid": "cea330ebdca015dc4aa64709f59b50683a4a3733", "dirty": false, "version": "0.5.3rc1", "error": null}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

