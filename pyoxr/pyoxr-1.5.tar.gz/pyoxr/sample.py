# -*- coding: utf-8 -*-
import pyoxr

if __name__ == "__main__":
    pyoxr.init("XXXXXXXX")
    a=pyoxr.OXRClient.get_latest(base="EUR", symbols="USD")
    print(a["rates"]["USD"])
