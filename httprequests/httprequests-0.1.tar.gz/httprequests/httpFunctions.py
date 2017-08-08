import requests
import json
from time import sleep
import sys
import argparse

#This function abstracts a post, put, or get request from the Requests library
#so that it can be done with one line of code while hiding all the details of 
#the Python Requests library

def request(IP, type, timeout = 5, msg = ""):
    #Make sure it handles json and raw strings
    if isinstance(msg, dict):
        msg=json.dumps(msg)
    else:
        msg = str(msg)

    if type.lower() == "post":
        try:
            r = requests.post(IP, msg, timeout = timeout)
            r.raise_for_status()
            print(r.status_code)
        except (requests.exceptions.ConnectionError):
            print("Connection Error")
        except (requests.exceptions.HTTPError):
            print("HTTP Error")
        except (requests.exceptions.Timeout):
            print("Timed out")
    elif type.lower() == "put":
        try:
            r = requests.put(IP, msg, timeout = timeout)
            r.raise_for_status()
            print(r.status_code)
        except (requests.exceptions.ConnectionError):
            print("Connection Error")
        except (requests.exceptions.HTTPError):
            print("HTTP Error")
        except (requests.exceptions.Timeout):
            print("Timed out")
    elif type.lower() == "get":
        try:
            r = requests.get(IP, timeout = timeout)
            r.raise_for_status()
            print(r.status_code)
            print(r.text)
        except (requests.exceptions.ConnectionError):
            print("Connection Error")
        except (requests.exceptions.HTTPError):
            print("HTTP Error")
        except (requests.exceptions.Timeout):
            print("Timed out")

def main(args):
    print(args)
    print(args[4])
    request(args[1], args[2], timeout = int(args[3]), msg = args[4])

if __name__ == "__main__":
    main(sys.argv)





