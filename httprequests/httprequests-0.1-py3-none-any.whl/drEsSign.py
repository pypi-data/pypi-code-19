from httprequests import httpFunctions

#Input: string with IP, ints for rgb
#Purpose: This function changes Dr E's Sign's lights to the rgb values input
def changeRGB(IP, red, green, blue):
    red = int(red)
    green = int(green)
    blue = int(blue)
    msg = "redVal=%s&greenVal=%s&blueVal=%s&"%(str(red), str(green), str(blue))
    httpFunctions.request(IP, "post", msg = msg)

#Input: string with IP, ints for rgb
#Purpose: This function adds (vals can be negative) the RGB values input to the
#current RGB vals of the sign
def addRGB(IP, red, green, blue):
    red = int(red)
    green = int(green)
    blue = int(blue)
    if red < 0:
        redSign = "N"
    else:
        redSign = "P"
    if green < 0:
        greenSign = "N"
    else:
        greenSign = "P"
    if blue < 0:
        blueSign = "N"
    else:
        blueSign = "P"

    msg = "redVal=%s&greenVal=%s&blueVal=%s&add%s%s%s"%(str(abs(red)), 
        str(abs(green)), str(abs(blue)), redSign, greenSign, blueSign)
    httpFunctions.request(IP, "post", msg = msg)

#Input: string with IP
#Purpose: Get information from an IP using an HTTP GET Request
def getInfo(IP):
    r = httpFunctions.request(IP, "get")
    return r

#In case it is called from command line.
def main(args):
    getInfo(args[1])

if __name__ == "__main__":
    main(sys.argv)
