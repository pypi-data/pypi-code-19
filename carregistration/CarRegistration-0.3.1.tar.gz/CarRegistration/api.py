import urllib2, base64, json

def CarRegistration(registrationNumber, username, password,endpoint):
    request = urllib2.Request("http://www.regcheck.org.uk/api/json.aspx/" + endpoint + "/" + registrationNumber)
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    result = urllib2.urlopen(request)
    data = json.load(result)
    return(data)
