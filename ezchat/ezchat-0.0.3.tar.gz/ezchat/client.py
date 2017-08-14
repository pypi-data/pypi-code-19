
import os
import logging

import flask
from flask import Flask, render_template, redirect, url_for, send_from_directory


logging.getLogger().setLevel(logging.DEBUG)


app = Flask(__name__, static_folder='./chatbox/dist')
app.config['DEBUG'] = True



# default route
@app.route('/', methods=['GET'])
def root():
    """single page app"""
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def send_asset(path):
    """All other static assets"""
    return app.send_static_file(path)


port = int(os.environ.get('port', 5001))
# print(port)

logging.info(app.config)
logging.info('Starting ezchat client')
app.run(debug=True, port=port)
