import pyximport; pyximport.install()

import json_parser
import io

import sys
import ujson

expr = {"id": True, "status": True}

import time
ti = time.perf_counter()

#for line in io.BufferedReader(sys.stdin):
for line in io.BufferedReader(open("/home/marcokawajiri/netshoes_20000", "rb")):
    parsed = ujson.loads(line)
    #print({"id": parsed["id"], "status": parsed["status"]})

print(time.perf_counter()-ti)