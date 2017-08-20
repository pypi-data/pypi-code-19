#!/usr/bin/env python

from gfiberspeedtest import run


print("Running speedtest")
result = run()
result_str = "Download speed: {}Mbps \nUpload speed: {}Mbps \nPing: {}ms"
print(result_str.format(result["download"], result["upload"],
                               result["ping"]))
