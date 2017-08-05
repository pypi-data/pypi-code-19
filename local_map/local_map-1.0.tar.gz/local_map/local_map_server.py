from flask import Flask
from flask import request
from flask import abort
import sqlite3
import sys
from flask import jsonify

port_number = None
if len(sys.argv) == 1:
    port_number = 12222
else:
    port_number = int(sys.argv[1])
db_name = 'local_map_server.db'
table_name = 'key_val_table'
host = '0.0.0.0'


conn = sqlite3.connect(db_name)
conn.execute('CREATE TABLE IF NOT EXISTS ' + table_name + ' (key TEXT, value TEXT);')
conn.close()

app = Flask(__name__)

@app.route('/<string:key>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def service(key):


    if request.method == 'GET':
        results = _get_from_db(table_name, key)
        return jsonify({'results':results})
    elif request.method == 'POST':
        if not request.json:
            abort(404)
        current = _get_from_db(table_name, key)
        if len(current) >= 1:
            abort(400)

        value = request.json['value']
        _insert_into_db(table_name, key, value)
        return jsonify(request.json)

    elif request.method == 'PUT':
        if not request.json:
            abort(404)
        current = _get_from_db(table_name, key)
        if len(current) == 0:
            abort(400)

        value = request.json['value']
        _update_value(table_name, key, value)
        return jsonify(request.json)

    elif request.method == 'DELETE':
        current = _get_from_db(table_name, key)
        if len(current) == 0:
            abort(400)

        _delete_entry(table_name, key)
        return 'Successfully deleted ' + key

def _delete_entry(table_name, key):
    conn = sqlite3.connect(db_name)
    conn.execute('DELETE FROM ' + table_name + ' WHERE key = \'' + key + '\';')
    conn.commit()
    conn.close()

def _update_value(table_name, key, value):
    conn = sqlite3.connect(db_name)
    conn.execute('UPDATE ' + table_name + ' SET value = \''+ value  + '\' WHERE key = \'' + key + '\';')
    conn.commit()
    conn.close()

def _insert_into_db(table_name, key, value):
    conn = sqlite3.connect(db_name)
    conn.execute('INSERT INTO ' + table_name + ' VALUES (\'' + key + '\', \'' + value  + '\');')
    conn.commit()
    conn.close()

def _get_from_db(table_name, key):
    conn = sqlite3.connect(db_name)
    cursor = conn.execute('SELECT * from ' + table_name + ' where key = \'' + key + '\';' )
    results = []
    for row in cursor:
        k = row[0]
        v = row[1]
        results.append({'key':k, 'value':v})
    conn.close()
    return results

if __name__ == '__main__':
    app.run(host=host, port=port_number)
