from httprequests import httpFunctions
import sys

#Input: IP for string, boolean for on/off status of the lights, int 0-255 for 
#saturation, int for hue, int 0-255 for brightness
#Purpose: Change the hue of the Philips Hue lightbulb
def changeHue(IP, on, sat, hue, bri):
    msg = {"on":on, "sat":sat, "hue":hue, "bri":bri}
    httpFunctions.request(IP, "put", msg = msg)

#Input: IP for string
#Purpose: Return info about Philips Hue Lightbulb. Note that IP address is
#different to the one used above.
def getInfo(IP):
    r = httpFunctions.request(IP, "get")
    return r

#In case it's called from command line
def main(args):
    getInfo(args[1])

if __name__ == "__main__":
    main(sys.argv)
