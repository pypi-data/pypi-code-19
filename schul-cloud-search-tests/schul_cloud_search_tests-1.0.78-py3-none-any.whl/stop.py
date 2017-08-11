import requests
import sys

requests.get("http://localhost:" + sys.argv[1] + "/stop")