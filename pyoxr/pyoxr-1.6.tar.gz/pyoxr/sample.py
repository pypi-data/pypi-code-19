# -*- coding: utf-8 -*-
import pyoxr

if __name__ == "__main__":
    pyoxr.init("XXXXX")
    try:
        response = pyoxr.OXRClient.get_latest(base="EUR", symbols="USD")
        print(response["rates"]["USD"])
    except pyoxr.OXRError as e:
        print(e)
