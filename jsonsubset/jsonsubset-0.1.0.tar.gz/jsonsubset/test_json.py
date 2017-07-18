import pyximport; pyximport.install()

import json_parser
import io

import sys
import json

expr = {"id": True, "status": True}

#for line in io.BufferedReader(sys.stdin):
for line in io.BufferedReader(open("/home/marcokawajiri/netshoes_20000", "rb")):
    parsed = json.loads(line.decode("utf-8"))