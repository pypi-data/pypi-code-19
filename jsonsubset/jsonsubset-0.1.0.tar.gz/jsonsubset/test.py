#import pyximport; pyximport.install()

from jsonsubset import subset
import io

import sys
import ujson

expr = {"id": True, "status": True, "auditInfo": {"updatedBy": True}}
expr = {"id": True, "status": True}

sub = subset.JsonSubset(expr)

import time
ti = time.perf_counter()
#for line in io.BufferedReader(sys.stdin):
for line in io.BufferedReader(open("/home/marcokawajiri/netshoes_20000", "rb")):
    parsed = sub.parse(line)
    #print(parsed)
    #print(ujson.dumps(parsed))
print(time.perf_counter()-ti)