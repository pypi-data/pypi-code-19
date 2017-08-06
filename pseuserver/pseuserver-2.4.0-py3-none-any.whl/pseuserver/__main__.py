
from flask import Flask
# from flask import abort, request, make_response, current_app , Response

# from pprint import pprint as pp
from pseuserver import *
import json
# from json import dumps
import argparse
# import os

# from functools import wraps, partial
# import re
# import operator
# from collections import Mapping
# from urllib.parse import urlparse, urljoin

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-P", "--port", type=int,
                    help="Customize the port")
    args = parser.parse_args()               
    _port = args.port or 5000
    app = Flask(__name__)
    restApi = PseuServer(app)
    app.run(debug=False, port = _port )
