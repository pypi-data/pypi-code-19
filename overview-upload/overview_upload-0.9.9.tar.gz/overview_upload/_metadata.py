import json
import sys

def parse_metadata_json(s, logger):
    try:
        d = json.loads(s)
    except json.JSONDecodeError as err:
        logger.error('Syntax error in metadata schema JSON at %d:%d: %s', err.lineno, err.colno, err.msg)
        sys.exit(1)

    if not isinstance(d, dict):
        logger.error('Error in metadata schema JSON: expected JSON Object')
        sys.exit(1)

    if sorted(d.keys()) != [ 'fields', 'version' ]:
        logger.error('Error in metadata schema JSON: expected "version" and "fields" properties, and no others')
        sys.exit(1)

    if d['version'] != 1:
        logger.error('Error in metadata schema JSON: "version" must be the Number 1')
        sys.exit(1)

    if not isinstance(d['fields'], list):
        logger.error('Error in metadata schema JSON: "fields" must be a JSON Array')
        sys.exit(1)

    for i, field in enumerate(d['fields']):
        if not isinstance(field, dict) or sorted(field.keys()) != [ 'display', 'name', 'type' ] or field['type'] != 'String' or not isinstance(field['name'], str):
            logger.error('Error in metadata schema JSON field %d: expected { "display": "TextInput", "type": "String", "name": "<name>" }', i)
            sys.exit(1)

    return d

def read_metadata_json_file(path, logger):
    try:
        with open(path, encoding='utf-8') as f:
            s = f.read()
    except IOError as err:
        logger.error('I/O Error %d reading metadata schema JSON file %s: %s', err.errno, err.filename, err.strerror)
        sys.exit(1)

    return parse_metadata_json(s, logger)

def parse_metadata_from_delimited_string_of_fields(s):
    names = [ name for name in map(str.strip, s.split(',')) if len(name) > 0 ]
    return {
        'version': 1,
        'fields': [ { 'name': name, 'type': 'String', 'display': 'TextInput' } for name in names ]
    }

DefaultMetadataSchema = { 'version': 1, 'fields': [] }
