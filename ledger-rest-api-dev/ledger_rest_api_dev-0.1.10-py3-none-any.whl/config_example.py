import os
from collections import OrderedDict

clientName = 'EvernymAgent'

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

genesisTxns = [{'txnId': '6b86b273ff34fce19d6b804eff5a3f57'
                         '47ada4eaa22f1d49c01e52ddb7875b4b',
                'type': 'NYM',
                'dest': 'o7z4QmFkNB+mVkFI2BwX0Hdm1BGhnz8psWnKYIXWTaQ=',
                'role': 'SPONSOR'}]


seedFileDir = "seed-files"
