def  sanitize(time_string):
    if '-' in time_string:
        spliter = '-'
    elif ':' in time_string:
        spliter = ':'
    else:
        return(time_string)
    (mins,secs) = time_string.split(spliter)
    return(mins +'.'+ secs)
