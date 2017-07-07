HTTP_CLIENT = "g.hc"
HTTP_SERVER = "g.http"

class InstanaSpan(object):
    t = 0
    p = None
    s = 0
    ts = 0
    ta = "py"
    d = 0
    n = None
    f = None
    ec = 0
    data = None

    def __init__(self, **kwds):
        self.__dict__.update(kwds)

class Data(object):
    service = None
    http = None
    baggage = None
    custom = None
    sdk = None

    def __init__(self, **kwds):
        self.__dict__.update(kwds)

class HttpData(object):
    host = None
    url = None
    status = 0
    method = None

    def __init__(self, **kwds):
        self.__dict__.update(kwds)

class CustomData(object):
    tags = None
    logs = None

    def __init__(self, **kwds):
        self.__dict__.update(kwds)

class SDKData(object):
    name = None
    Type = None
    arguments = None
    Return = None
    custom = None

    def __init__(self, **kwds):
        self.__dict__.update(kwds)
