from typing import Mapping, List

from plenum.common.constants import REQNACK
from plenum.common.request import Request
from plenum.common.types import Reply, OP_FIELD_NAME
from plenum.common.util import getMaxFailures

from sovrin_client.client.client import Client
from stp_core.common.log import getlogger

from sovrin_client_rest.client_storage import ClientStorage

logger = getlogger()


class PersistentClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage = ClientStorage(self.name)
        self.lastReqId = self.storage.getLastReqId()

    def submit(self, *operations: Mapping) -> List[Request]:
        requests = super().submit(*operations)
        for r in requests:
            self.storage.addRequest(r)
        return requests

    def handleOneNodeMsg(self, wrappedMsg) -> None:
        """
        Handles single message from a node, and appends it to a queue

        :param wrappedMsg: Reply received by the client from the node
        """
        super().handleOneNodeMsg(wrappedMsg)
        msg, frm = self.inBox[-1]
        op = msg[OP_FIELD_NAME]
        if op == Reply.typename:
            self.storage.addReply(msg, frm)
        elif op == REQNACK:
            self.storage.addNack(msg, frm)

    def replyIfConsensus(self, reqId: int):
        f = getMaxFailures(len(self.nodeReg))
        replies, errors = self.storage.getAllReplies(reqId)
        r = list(replies.values())[0] if len(replies) > f else None
        e = list(errors.values())[0] if len(errors) > f else None
        return r, e

    def hasMadeRequest(self, reqId):
        return self.storage.hasRequest(reqId)
