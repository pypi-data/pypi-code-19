from httprequests import httpFunctions
#OG: import httpFunctions

def changeRGB(IP, red, green, blue):
    red = int(red)
    green = int(green)
    blue = int(blue)
    msg = "redVal=%s&greenVal=%s&blueVal=%s&"%(str(red), str(green), str(blue))
    httpFunctions.request(IP, "post", msg = msg)

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

def getInfo(IP):
    httpFunctions.request(IP, "get")

def main(args):
    getInfo(args[1])

if __name__ == "__main__":
    main(sys.argv)
