from bottle import get, run, response, request
import json


@get("/<path:path>")
def get(path):
    """Return a search response."""
    response.set_header("Content-Type", "application/vnd.api+json")
    self_href = "http://" + request.headers.get("host", "localhost") + "?" + request.query_string
    result = {
        "jsonapi": {
            "version": "1.0",
            "meta": {
                "name": "schul_cloud/schul_cloud_search_tests", 
                "source": 
                    "https://github.com/schul_cloud/schul_cloud_search_tests",
                "description":
                    "These are the tests for the search engines.",
            }
        },
        "links" : {
            "self": {
                 "href": self_href,
                 "meta": {
                    "limit": 10,
                    "offset": 0,
                    "count": 0
                 }
            },
            "first": None,
            "last": None,
            "prev": None,
            "next": None,
        },
        "data": []
    }
    return json.dumps(result)

if __name__ == "__main__":
    run(reload=True, port=8080)
