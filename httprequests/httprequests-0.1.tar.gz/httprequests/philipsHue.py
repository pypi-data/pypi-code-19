from httprequests import httpFunctions
import sys

def changeHue(IP, on, sat, hue, bri):
    msg = {"on":on, "sat":sat, "hue":hue, "bri":bri}
    httpFunctions.request(IP, "put", msg = msg)

def getInfo(IP):
    httpFunctions.request(IP, "get")

def main(args):
    getInfo(args[1])

if __name__ == "__main__":
    main(sys.argv)
