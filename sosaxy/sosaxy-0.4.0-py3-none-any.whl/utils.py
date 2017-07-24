import json

def write_json(f, record):
    s = json.dumps(record)
    f.write(s)
    f.write('\n')
