import glob
import os
import jsonpickle

import sovrin_client_rest
from plenum.common.request import Request
from sovrin_client_rest.exceptions import RequestNotFound


class ClientStorage:
    dataLocation = "data/clients"
    basePath = os.path.dirname(sovrin_client_rest.__file__)

    def __init__(self, clientId):
        self.clientDataLocation = ClientStorage.getDataLocation(clientId)
        if not os.path.exists(self.clientDataLocation):
            os.makedirs(self.clientDataLocation)

    def getRequestFilePath(self, reqId: int) -> str:
        fileName = "{}.json".format(str(reqId))
        return os.path.join(self.clientDataLocation, fileName)

    def hasRequest(self, reqId):
        requestPath = self.getRequestFilePath(reqId)
        return os.path.exists(requestPath)

    def readData(self, reqId: int):
        try:
            with open(self.getRequestFilePath(reqId), "r") as file:
                data = jsonpickle.loads(file.read())
            return data
        except FileNotFoundError:
            RequestNotFound()

    def writeData(self, reqId: int, data):
        with open(self.getRequestFilePath(reqId), "w") as file:
            file.write(data)

    def addRequest(self, request: Request):
        data = jsonpickle.dumps({
            "request": request.__dict__,
            "results": {}
        })
        self.writeData(request.reqId, data)

    def addResult(self, reply, frm: str, storekey='results', readkey='result'):
        reqId = reply['reqId']
        data = self.readData(reqId)
        if storekey not in data:
            data[storekey] = {}
        data[storekey][frm] = reply[readkey]
        self.writeData(reqId, jsonpickle.dumps(data))

    def addReply(self, reply, frm: str):
        self.addResult(reply, frm)

    def addNack(self, reply, frm: str):
        self.addResult(reply, frm, 'errors', 'reason')

    def getAllReplies(self, reqId):
        try:
            data = self.readData(reqId)
        except RequestNotFound as ex:
            raise ex
        r = data['results'] if data and 'results' in data else {}
        e = data['errors'] if data and 'errors' in data else {}
        return r, e

    def getLastReqId(self):
        curdir = os.curdir
        os.chdir(self.clientDataLocation)
        reqIds = [int(name.split(".")[0]) for name in glob.glob("*.json")]
        os.chdir(curdir)
        return max(reqIds) if len(reqIds) > 0 else 0

    @classmethod
    def getDataLocation(cls, clientId):
        return os.path.join(cls.basePath, cls.dataLocation, clientId)
