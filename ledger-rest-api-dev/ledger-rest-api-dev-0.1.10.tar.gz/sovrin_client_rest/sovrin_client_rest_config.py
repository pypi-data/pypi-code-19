from collections import OrderedDict

clientName = 'EvernymRestClient'

clientSeed = 'g034OTmx7qBRtywvCbKhjfALHnsdcJpl'

nodeReg = OrderedDict([
    ('Node1', ('127.0.0.1', 9701)),
    ('Node2', ('127.0.0.1', 9703)),
    ('Node3', ('127.0.0.1', 9705)),
    ('Node4', ('127.0.0.1', 9707))
])

serverAddr = ("127.0.0.1", 8888)

clientToPoolAddr = ('0.0.0.0', 9700)

baseDataDir = "~/.sovrin"

seedFileDir = "seed-files"
