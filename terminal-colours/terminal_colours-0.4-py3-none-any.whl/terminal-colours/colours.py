class Colours:
    # attributes off
    off = "\033[0m"

    # attributes
    bold = "\033[1m"
    boldOFF = "\033[21m"
    underline = "\033[4m"
    underlineOFF = "\033[24m"
    reverse = "\033[7m"

    # foreground colours
    blackF = "\033[30m"
    redF = "\033[31m"
    greenF = "\033[32m"
    yellowF = "\033[33m"
    blueF = "\033[34m"
    magentaF = "\033[35m"
    cyanF = "\033[36m"
    whiteF = "\033[37m"

    # background colours
    blackB = "\033[40m"
    redB = "\033[41m"
    greenB = "\033[42m"
    yellowB = "\033[43m"
    blueB = "\033[44m"
    magentaB = "\033[45m"
    cyanB = "\033[46m"
    whiteB = "\033[47m"

    # mixed colours
    blackWHITE = blackF + whiteB
    blackYELLOW = blackF + yellowB
    blackGREEN = blackF + greenB
    blueWHITE = blueF + whiteB
    cyanWHITE = cyanF + whiteB
    greenWHITE = greenF + whiteB
    magentaWHITE = magentaF + whiteB
    redBLACK = redF + blackB
    redBLUE = redF + blueB
    redWHITE = redF + whiteB
    whiteRED = whiteF + redB
    whiteGREEN = whiteF + greenB
    whiteBLACK = whiteF + blackB
    yellowWHITE = yellowF + whiteB
