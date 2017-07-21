from bottle import get, run, response, request
import json
from schul_cloud_resources_api_v1.schema import get_schemas


@get("/<path:path>")
def get(path):
    """Return a search response."""
    response.set_header("Content-Type", "application/vnd.api+json")
    self_href = "http://" + request.headers.get("host", "localhost") + "?" + request.query_string
    example_resources = get_schemas()["resource"].get_valid_examples()
    resources = [{"type":"resource","attributes":data,"id":str(i)}
                 for i, data in enumerate(example_resources)]
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
                    "count": len(resources)
                 }
            },
            "first": self_href,
            "last": self_href,
            "prev": None,
            "next": None,
        },
        "data": resources
    }
    return json.dumps(result)

if __name__ == "__main__":
    run(reload=True, port=8080)
