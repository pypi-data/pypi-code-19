from bottle import (
    Bottle, request, response, redirect, static_file, SimpleTemplate
)
import sys
import os
import shutil
import requests
try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError
from schul_cloud_resources_server_tests.tests.fixtures import StoppableWSGIRefServerAdapter
if "" in sys.path:
    sys.path.append(".")
from schul_cloud_search_tests.search_tests import run_request_tests, run_response_tests

ENDPOINT_STOP = "/stop"
ENDPOINT_CODE = ["/code", "/code/", "/code/<path:path>", "/code<ending:re:\\.zip>"]
REDIRECT_TO = "http://localhost:8080"
APPLICATION = "schul_cloud_search_tests"
HERE = os.path.dirname(__file__)
LISTING_TEMPLATE = SimpleTemplate(
"""
% import os
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
  </head>
  <body>
    <h1>{{ APPLICATION }}</h1>
    <p>
      You can view the updated source code on
      <a href="https://github.com/schul-cloud/schul_cloud_search_tests">GitHub</a>, create issues and get in touch with the developers.
      You can find the currently running version below.
      You can <a href="/code.zip">download the currently running version of the service</a>.
    </p>
    <ul>
    % for dirpath, dirnames, filenames in os.walk(here):
      % assert dirpath.startswith(here)
      % dirpath = dirpath[len(here):]
      % dirpath = dirpath.replace("\\\\", "/")
      % for filename in filenames:
        % if filename.endswith(".pyc"):
          % continue
        % end
        % file = dirpath + "/" + filename
        <li>
          <a href="/code{{ file }}">{{ file }}</a>
        </li>      
      % end
    % end
    </ul>
    <p>
    </p>
  </body>
</html>
""")


def pytest_errors(status, errors, server_url, answer=None, secret=""):
    """Return the formatted pytest errors, jsonapi compatible."""
    response.status = status
    error_text = ("Bad Request" if status == 400 else "Conflict")
    code = "http://" + request.headers["host"] + "/code"
    result = {
      "errors":[
        {
          "status": str(status),
          "title": error_text,
          "detail": "The request or response contained some errors.",
          "meta": {
            "url": server_url,
            "response": answer
          }
        }
      ] + errors,
      "jsonapi": {
        "version": "1.0",
        "meta": {
          "name": "schul_cloud/schul_cloud_search_tests", 
          "source": code,
          "description":
            "These are the tests for the search engines.",
          "secret": secret
        }
      }
    }
    return result


def check_response(target_url, secret=""):
    """Test the request and the response to the search engine."""
    print("query string:", request.query_string)
    server_url = target_url + "?" + request.query_string
    client_errors = run_request_tests(server_url)
    return_error = (400 if client_errors else 409)
    answer = requests.get(server_url, headers=request.headers)
    server_errors = run_response_tests(server_url, answer)
    try:
        result = answer.json()
    except (JSONDecodeError):
        result = None
    if client_errors and answer.status_code != 400 or server_errors:
        errors = client_errors + server_errors
        return pytest_errors(return_error, errors, server_url, result,
                             secret=secret)
    assert result is not None, "The tests take care that there is a result."
    response.status = answer.status_code
    return result


def get_code(path=None, ending=None):
    """Return a directory listing or a static file."""
    if ending is not None:
        assert ending == ".zip"
        redirect("/code/{}.zip".format(APPLICATION))
    if path == APPLICATION + ".zip":
        # Download the source of this application."""
        # from http://stackoverflow.com/questions/458436/adding-folders-to-a-zip-file-using-python#6511788
        zip_path = (shutil.make_archive("/tmp/" + APPLICATION, "zip", HERE))
        return static_file(zip_path, root="/")
    if path is None:
        path = "/"
    if path.endswith("/"):
        # return a listing
        allowed = ["/", "tests/", "search_tests/"]
        assert path in allowed, "Path \"{}\" should be in {}".format(path, allowed)
        return LISTING_TEMPLATE.render(here=HERE, APPLICATION=APPLICATION)
    return static_file(path, root=HERE)


def get_app(endpoint="/", target_url="http://localhost:8080", secret=""):
    """Return a bottle app that tests the request and the response."""
    app = Bottle()
    app.get(endpoint, callback=lambda: check_response(target_url, secret=secret))
    for code_endpoint in ENDPOINT_CODE:
        app.get(code_endpoint, callback=get_code)
    return app


def run(app, host="0.0.0.0", port=8081):
    """Run a stoppable bottle app."""
    server = StoppableWSGIRefServerAdapter(host=host, port=port)
    app.get(ENDPOINT_STOP, callback=lambda: server.shutdown(blocking=False))
    app.run(debug=True, server=server)


def main(host="0.0.0.0", port=8081, endpoint="/", target_url="http://localhost:8080"):
    """Start the server."""
    app = get_app(endpoint=endpoint, target_url=target_url)
    run(app, host=host, port=port)


__all__ = ["main", "run", "get_app"]

if __name__ == "__main__":
    kw = {"host": "0.0.0.0"}
    kw["target_url"] = (sys.argv[1] if len(sys.argv) >= 2 else "http://localhost:8080/v1/search")
    kw["port"] = (int(sys.argv[2]) if len(sys.argv) >= 3 else 8081) 
    kw["endpoint"] = (sys.argv[3] if len(sys.argv) >= 4 else "/v1/search")
    print("Forwarding traffic from http://{host}:{port}{endpoint} to {target_url}".format(**kw))
    main(**kw)
