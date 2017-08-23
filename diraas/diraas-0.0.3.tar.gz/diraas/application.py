import glob
import os.path as op
from functools import reduce
import operator

from flask import Flask, jsonify, request
from werkzeug.exceptions import BadRequest, Forbidden, InternalServerError

app = Flask('diraas')


@app.before_request
def check_token():
    if not app.config['ACCESS_TOKEN']:
        return

    if not request.args.get('token') == app.config['ACCESS_TOKEN']:
        raise Forbidden('Token mismatch')


def path_sanitize(path):
    path = path.lstrip(op.sep)
    if '..' in path:
        raise Forbidden('.. is not allowed in path!')
    return path


@app.route('/ls')
def ls():
    root_dir = app.config['ROOT_DIR']
    targets = request.args.get('targets')

    if not targets:
        raise BadRequest('targets required!')

    ret = reduce(operator.add, [
        glob.glob(op.join(root_dir, path_sanitize(t)))
        for t in targets.split()
    ])
    ret = [p.replace(root_dir, '').lstrip(op.sep) for p in ret]

    return jsonify(ret)


@app.route('/fetch')
def fetch():
    root_dir = app.config['ROOT_DIR']
    targets = request.args.get('targets')

    if not targets:
        raise BadRequest('targets required!')

    try:
        ret = {
            p: open(op.join(root_dir, path_sanitize(p))).read()
            for p in targets.split()
        }
    except IOError as e:
        raise InternalServerError(e)

    return jsonify(ret)
