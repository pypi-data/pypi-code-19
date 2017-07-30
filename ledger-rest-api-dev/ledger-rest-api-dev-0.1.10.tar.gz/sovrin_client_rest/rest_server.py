import sys
import traceback
import asyncio
import json

import time
from typing import Dict

from aiohttp import web
from sovrin_common.config_util import getConfig as clientConfig
from sovrin_common.constants import ATTRIB
from stp_core.common.log import getlogger
from stp_core.network.port_dispenser import genHa

from plenum.common.constants import IDENTIFIER, TYPE, TARGET_NYM, TXN_ID, \
    DATA, TXN_TYPE, ROLE, ENC, RAW, HASH, VERKEY, TXN_TIME, NAME
from plenum.common.types import f
from sovrin_common.transactions import SovrinTransactions

from sovrin_client.client.client import Client
from sovrin_client_rest.exceptions import RequestNotFound, SeedFileNotFound
from sovrin_client_rest.wallet_operation_builder import get_prepared_req, \
    OP_DATA

logger = getlogger()

NO_REPLY_RECEIVED = "No reply received"
NO_ERROR_RECEIVED = "No error received"
clientConfig = clientConfig()


class RestServer:
    def __init__(self,
                 config,
                 looper,
                 serverAddr=None):

        self.looper = looper
        self.config = config
        self.clients = {}

        if serverAddr:
            self.serverAddr = serverAddr
        else:
            self.serverAddr = config.serverAddr

        self.printSpecificConfigValues()

        asyncio.ensure_future(self.start())

    @staticmethod
    def printSpecificConfigValues():
        keys = ["baseDir", "cliNodeReg", "nodeReg", "poolTransactionsFile"]
        print("## Client config values: ")
        for k in keys:
            print("  ## {}: {}".format(k, getattr(clientConfig, k)))

    @asyncio.coroutine
    def index(self, request):
        d = b"""
            <html>
            <head>
            </head>
            <body>
                <h1>REST wrapper for Sovrin Client</h1>
                <ul>
                    <li>
                        <b>POST</b> <i>/transaction</i> (Create a transaction)<br/>
                        Arguments
                        <ul>
                            <li>
                                clientId: str
                            </li>
                            <li>
                                operation: JSON
                            </li>
                        </ul>
                    </li>
                    <li>
                        <b>GET</b>
                        <i>/transaction/client/&lt;clientId&gt;/request/&lt;requestId&gt;</i> (
                        Read results of an already
                        made
                        transaction)<br/>
                    </li>
                </ul>
            </body>
        </html>
        """
        return web.Response(body=d)

    async def start(self):
        app = web.Application(loop=self.looper.loop)

        app.router.add_route('POST', '/txn', self.add_txn_req_handler)
        app.router.add_route('POST', '/nym/{dest}', self.add_nym_req_handler)
        app.router.add_route('POST', '/nym/{dest}/{attr}', self.add_attr_to_nym_req_handler)
        app.router.add_route('GET', '/txn/{txnId}', self.get_txn_by_txn_id_req_handler)
        app.router.add_route("GET",
                             "/txn/identifier/{identifier}/request/{reqId}",
                             self.get_txn_by_req_id_handler)
        app.router.add_route("GET", "/nym/{nym}/attr/{attribute}", self.get_attr_req_handler)
        #app.router.add_route("GET", "/nym/{nym}/attr", self.build_and_execute_req)
        app.router.add_route("GET", "/nym/{nym}", self.get_nym_req_handler)
        #app.router.add_route('GET', '/nym/{nym}/verify', self.build_and_execute_req)
        app.router.add_route('GET', '/', self.index)

        host, port = self.serverAddr
        srv = await self.looper.loop.create_server(app.make_handler(),
                                            host, port)
        print("Server started at http://%s:%s" % (host, port))
        return srv

    @staticmethod
    def send_timeout_if_needed(reply, error):
        if reply is None and error is None:
            return RestServer.api_response(status=504, body={
                "error": "No response received from nodes"})

    @staticmethod
    def api_response(status=200, body=None):
        params = {
            "status": status,
            "content_type": "application/json",
            "charset": "utf-8"
        }
        if body:
            if isinstance(body, (dict, list, tuple)):
                body = json.dumps(body)
            if not isinstance(body, bytes):
                body = body.encode()
            params["body"] = body

        return web.Response(**params)

    @staticmethod
    def build_req_data(id, typ):
        return {
            OP_DATA: {
                TYPE: typ.value
            },
            IDENTIFIER: id
        }

    @staticmethod
    def get_query_param_by_name(api_req, paramName, required=True):
        try:
            value = api_req.rel_url.query[paramName]
        except KeyError:
            value = None
        if required:
            assert value is not None
        return value

    @staticmethod
    def get_path_segment_by_attr_name(api_req, attrName, required=True):
        getData = api_req.match_info
        value = getData.get(attrName, None)
        if required:
            assert value is not None
        return value

    @staticmethod
    def get_txns(client, reqId):
        txns = []
        for val in client.txnLog.transactionLog.iterator(includeKey=False,
                                                includeValue=True):
            txn = client.txnLog.serializer.deserialize(val, fields=client.txnLog.txnFieldOrdering)
            data = json.loads(txn[DATA]) if txn[DATA] else None
            txn[DATA] = data
            if txn.get(f.REQ_ID.nm) == reqId:
                txns.append(txn)

        return txns

    @staticmethod
    def is_reply_present(client, reqId):
        txns = RestServer.get_txns(client, reqId)
        if len(txns) > 0:
            return True
        else:
            return False

    @staticmethod
    def get_identifier_from_header(request):
        id = request.headers.get(IDENTIFIER, None)
        return id

    @staticmethod
    def required_param_not_found(argName):
        errorMsg = {"error": "'{}' should be present in request arguments".
            format(argName)}
        return RestServer.api_response(status=400, body=errorMsg)

    @staticmethod
    def build_response(reply, specific_fields=[]):
        resp = {}
        common_fields = [TXN_ID, TXN_TIME, TXN_TYPE, IDENTIFIER, TARGET_NYM, DATA,
                         f.REQ_ID.nm, f.SEQ_NO.nm]
        all_fields = common_fields + specific_fields
        for name in all_fields:
            if reply.get(name, None):
                resp[name] = reply[name]
        return resp

    @staticmethod
    def _prepare_op_data(req_data):
        # TODO: Add support for RAW and HASH, would require changes in Catalyst
        # Validate operation is in correct format.
        op_data = req_data[OP_DATA]
        if op_data.get(ENC):
            attr = op_data[ENC]
            try:
                # Strict is set to false since provided json can have
                # control characters like `\n` and `t`
                parsed = json.loads(attr, strict=False)
            except ValueError:
                errorMsg = "Invalid attribute: {}".format(attr)
                return None, RestServer.api_response(status=400,
                                               body={"error": errorMsg})
            # TODO: Temporary fix to escape potential unescaped control
            # characters like `\n` and `t`. Get this fixed from the client of
            # this api(Catalyst)
            op_data[ENC] = json.dumps(parsed)
        return req_data, None

    async def build_and_execute_req(self, api_req, req_data, resp_handler):
        try:
            logger.debug("initial sov operation: {}".format(req_data))
            identifier = self.get_req_identifier(req_data)
            client = self.get_client_by_identifier(identifier)

            if client.name not in [p.name for p in self.looper.prodables]:
                self.looper.add(client)

            if req_data.get(OP_DATA) or req_data.get(f.REQ_ID.nm):
                client, client_req, reply, error = await self.submit_req(client, req_data)
            else:
                client, client_req, reply, error = client, req_data, None, None

            if req_data.get(OP_DATA, None):
                timeout_error = self.send_timeout_if_needed(reply, error)
                if timeout_error:
                    return timeout_error
                elif error:
                    return RestServer.api_response(status=404, body={"error": error})

            return await resp_handler(api_req, client_req, client, reply, error)
        except SeedFileNotFound as sf:
            return RestServer.api_response(status=500, body={
                "error": "error occurred during executing request: {}, "
                         "\n info: {}".format(str(req_data), str(sf))})
        except:
            err_info = traceback.format_exc(sys.exc_info())
            return RestServer.api_response(status=500, body={
                "error": "error occurred during executing request: {}, "
                         "\n info: {}".format(str(req_data), err_info)})

    async def get_nym_req_handler(self, api_req):
        id = self.get_path_segment_by_attr_name(api_req, 'nym')
        req_data = self.build_req_data(id, SovrinTransactions.GET_NYM)
        return await self.build_and_execute_req(api_req, req_data,
                                      self.get_nym_resp_handler)

    async def get_nym_resp_handler(self, api_req, client_req, client, reply,
                                   error):
        resp_body = self.build_response(reply)
        if reply[DATA] is None:
            status = 404
        else:
            status = 200
        return self.api_response(status=status, body=resp_body)

    async def get_attr_req_handler(self, api_req):
        getData = api_req.match_info
        dest = getData.get("nym", None)
        attribute = getData.get('attribute', None)
        id = self.get_identifier_from_header(api_req)
        if id is None:
            return RestServer.api_response(status=400, body=
            {"error": "'{}' is required in header".format(IDENTIFIER)})
        req_data = self.build_req_data(id, SovrinTransactions.GET_ATTR)
        req_data[OP_DATA][TARGET_NYM] = dest
        req_data[OP_DATA][NAME] = attribute
        return await self.build_and_execute_req(api_req, req_data,
                                                self.get_attr_resp_handler)

    async def get_attr_resp_handler(self, api_request, client_req, client,
                                   reply, error):
        resp_body = self.build_response(reply)
        if reply[DATA] is None:
            status = 404
        else:
            status = 200
        return self.api_response(status=status, body=resp_body)

    async def add_nym_req_handler(self, api_req):
        dest = self.get_path_segment_by_attr_name(api_req, 'dest')
        id = self.get_identifier_from_header(api_req)
        ver_key = self.get_query_param_by_name(api_req, "verkey")
        if id is None:
            return RestServer.api_response(status=400, body=
            {"error": "'{}' is required in header".format(IDENTIFIER)})
        op = self.build_req_data(id, SovrinTransactions.NYM)
        op[OP_DATA][TARGET_NYM] = dest
        op[OP_DATA][VERKEY] = ver_key
        return await self.build_and_execute_req(api_req, op,
                                      self.add_nym_resp_handler)

    async def add_nym_resp_handler(self, api_request, client_req, client,
                                   reply, error):
        resp_body = self.build_response(reply)
        if reply[f.SEQ_NO.nm] is None:
            status = 500
        else:
            status = 201
        return self.api_response(status=status, body=resp_body)

    async def get_txn_by_req_id_handler(self, api_req):
        getData = api_req.match_info
        identifier = getData['identifier']
        reqId = getData['reqId']
        req_data = {
            IDENTIFIER: identifier,
            f.REQ_ID.nm: reqId
        }
        return await self.build_and_execute_req(api_req, req_data,
                                      self.get_txn_by_req_id_resp_handler)

    async def get_txn_by_req_id_resp_handler(self, api_req, client_req, client,
                                             reply, error):
        resp_body = self.build_response(reply)
        return self.api_response(body=resp_body)

    @staticmethod
    def build_common_req_data(post_data):
        fields = (TXN_TYPE, VERKEY, TARGET_NYM, ROLE, ENC, RAW, HASH)
        req_data = {OP_DATA: {}}
        for f in fields:
            val = post_data.get(f)
            # Request must contain TXN_TYPE in POST body.
            if f == TXN_TYPE:
                if not val:
                    return None, RestServer.required_param_not_found(f)
            req_data[OP_DATA][f] = val

        return req_data, None

    async def add_txn_req_handler(self, api_req):
        post_data = await api_req.post()
        common_req_data, err_resp = self.build_common_req_data(post_data)
        if err_resp:
            return err_resp

        req_data, err_resp = self._prepare_op_data(common_req_data)
        if err_resp:
            return err_resp

        id = self.get_identifier_from_header(api_req)
        if id is None:
            return RestServer.api_response(status=400, body=
            {"error": "'{}' is required in header".format(IDENTIFIER)})
        req_data[IDENTIFIER] = id
        return await self.build_and_execute_req(api_req, req_data,
                                      self.get_txn_by_req_id_resp_handler)

    async def get_txn_by_txn_id_req_handler(self, api_req):
        getData = api_req.match_info
        txnId = getData['txnId']
        id = self.get_identifier_from_header(api_req)
        if id is None:
            return RestServer.api_response(status=400, body=
            {"error": "'{}' is required in header".format(IDENTIFIER)})
        client = self.get_client_by_identifier(id)
        txn = RestServer.get_txns(client, txnId)[0]
        if txn:
            try:
                txn[TXN_TIME] = txn[TXN_TIME].strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                pass
            return self.api_response(status=200, body=txn)
        else:
            return self.api_response(status=404)

    async def add_attr_to_nym_req_handler(self, api_req):
        id = self.get_identifier_from_header(api_req)
        if id is None:
            return RestServer.api_response(status=400, body=
            {"error": "'{}' is required in header".format(IDENTIFIER)})
        post_data = {
            TXN_TYPE: ATTRIB,
            TARGET_NYM: api_req.match_info[TARGET_NYM],
            ENC: api_req.match_info['attr'],
            IDENTIFIER: id
        }
        common_req_data, err_resp = self.build_common_req_data(post_data)
        if err_resp:
            return err_resp
        req_data, err_resp = self._prepare_op_data(common_req_data)
        if err_resp:
            return err_resp

        req_data[IDENTIFIER] = id
        return await self.build_and_execute_req(api_req, req_data,
                                                self.get_txn_by_req_id_resp_handler)

    @staticmethod
    def get_req_identifier(request):
        return request.get(IDENTIFIER)

    def build_client(self, identifier):
        logger.debug('basedir: {}'.format(clientConfig.baseDir))
        client = Client(identifier,
                        nodeReg=None,
                        ha=genHa(),
                        config=clientConfig)
        self.clients[identifier] = client
        return client

    def get_client_by_identifier(self, identifier):
        client = self.clients.get(identifier)
        if client:
            return client
        else:
            return self.build_client(identifier)

    async def submit_req(self, client, client_req):
        reply, error, req_id = None, None, None
        identifier = self.get_req_identifier(client_req)
        if client_req.get(OP_DATA):
            client_req = await get_prepared_req(identifier, client_req)
            logger.debug("client request: {}".format(client_req))
            req, = client.submitReqs(client_req)
            req_id = req.reqId
        elif client_req.get(f.REQ_ID.nm):
            req_id = client_req.get(f.REQ_ID.nm)

        # Let the request reach the nodes and processing happen
        start = time.perf_counter()
        longTimeout = 20
        elapsed = 0

        while elapsed < longTimeout:
            try:
                reply, error = client.replyIfConsensus(identifier,
                                                       req_id)
            except RequestNotFound as ex:
                return RestServer.api_response(status=404,
                                               body={"error": ex.msg})
            except Exception as ex:
                return RestServer.api_response(status=500,
                                               body={"error": str(ex)})
            if reply or error:
                break
            await asyncio.sleep(.25)
            elapsed = time.perf_counter() - start

        return client, client_req, reply, error

    #
    #
    # # TODO: NEED TO FIND A WAY TO TAKE OUT THE VALIDATION CODE FROM HANDLEERS.
    # # LOTS OF BOILERPLATE CODE
    #
    # async def addNym(self, request):
    #     op = {}
    #     op[TXN_TYPE] = NYM
    #     op['dest'] = request.match_info[TARGET_NYM]
    #
    #     assert len(self.client.signers) == 1  # assume only one signer
    #     signer = next(iter(self.client.signers.values()))
    #     op[ORIGIN] = signer.verstr
    #
    #     return await self._add(self.client, self.longTimeout, op)
    #
    # async def addAttrToNym(self, request):
    #     op = {
    #         TXN_TYPE: ATTRIB,
    #         TARGET_NYM: request.match_info[TARGET_NYM],
    #         ENC: request.match_info['attr']
    #     }
    #     assert len(self.client.signers) == 1  # assume only one signer
    #     signer = next(iter(self.client.signers.values()))
    #     op[ORIGIN] = signer.verstr
    #
    #     return await self._add(self.client, self.longTimeout, op)
    #


    #
    # async def getAttribute(self, request):
    #     getData = request.match_info
    #     nym = getData.get("nym", None)
    #     attribute = getData.get('attribute', None)
    #
    #     identifier = self.getIdentifierFromHeader(request)
    #
    #     if identifier and identifier not in self.client.signers:
    #         errorMsg = {"error": "Invalid identifier {}".format(identifier)}
    #         return self.apiResponse(status=400, body=errorMsg)
    #
    #     attr = self.client.getAttributeForNym(nym, attribute,
    #                                           identifier=identifier)
    #     if attr:
    #         return self.apiResponse(body=attr)
    #     else:
    #         return self.apiResponse(status=404,
    #                             body={"error": "Attribute not found"})
    #
    # async def getAttributes(self, request):
    #     getData = request.match_info
    #     nym = getData.get('nym', None)
    #
    #     identifier = self.getIdentifierFromHeader(request)
    #
    #     if identifier and identifier not in self.client.signers:
    #         errorMsg = {"error": "Invalid identifier {}".format(identifier)}
    #         return self.apiResponse(status=400, body=errorMsg)
    #
    #     attributes = self.client.getAllAttributesForNym(nym,
    #                                                     identifier=identifier)
    #     if attributes:
    #         return self.apiResponse(status=200,
    #                             body=attributes)
    #     else:
    #         return self.apiResponse(status=204)
    #
    #
    #
    # async def verifyToken(self, request):
    #     getData = request.match_info
    #     nym = getData.get('nym', None)
    #     signature = request.GET.get('signature')
    #     challenge = request.GET.get('challenge')
    #     if not signature:
    #         return self.requiredParamNotFound("signature")
    #     if not challenge:
    #         return self.requiredParamNotFound("challenge")
    #
    #     ser = challenge.encode()
    #     hasNym = await self.getNymEventually(nym)
    #     if hasNym:
    #         verKeyAttr = self.client.getAttributeForNym(nym, 'verKey')
    #         if verKeyAttr is not None:
    #             verKey = next(iter(verKeyAttr.values()))
    #         else:
    #             verKey = nym
    #         vr = Verifier(self.b64toBytes(verKey))
    #         isVerified = vr.verify(self.b64toBytes(signature), ser)
    #         return self.apiResponse(body={'verified': isVerified})
    #     else:
    #         return self.apiResponse(status=404, body="Nym not found")
    #
    # @staticmethod
    # def b64toBytes(string):
    #     return base64_decode(string.encode())
    #
    #
    #
    # async def getNym(self, request):
    #     getData = request.match_info
    #     nym = getData.get('nym', None)
    #     identifier = self.client.defaultIdentifier
    #     nymPresent = await self.getNymEventually(nym, identifier)
    #     version = 2 if "Accept" in request.headers and \
    #                    request.headers["Accept"] == \
    #                    "application/vnd.sovrin-rest-client.v2+json" else 1
    #     if version == 2:
    #         status = 204 if nymPresent else 404
    #         return self.apiResponse(status=status)
    #     else:
    #         response = {"success": nymPresent}
    #         return self.apiResponse(body=response)
    #
    # async def getNymEventually(self, nym, identifier=None, timeout=5):
    #     identifier = identifier if identifier else self.client.defaultIdentifier
    #     if self.client.hasNym(nym):
    #         return True
    #     else:
    #         self.client.doGetNym(nym, identifier)
    #         return await self.hasNymEventually(nym, timeout)
    #
    # async def hasNymEventually(self, nym, timeout=5):
    #     nymPresent = False
    #     start = time.perf_counter()
    #     elapsed = 0
    #     while elapsed < timeout:
    #         nymPresent = self.client.hasNym(nym)
    #         if nymPresent:
    #             break
    #         await asyncio.sleep(.1)
    #         elapsed = time.perf_counter() - start
    #     return nymPresent
    #
    #
    # @staticmethod
    # async def _add(client, longTimeout, op):
    #     # TODO: Add support for RAW and HASH, would require changes in Catalyst
    #     # Validate operation is in correct format.
    #     if ENC in op:
    #         attr = op[ENC]
    #         try:
    #             # Strict is set to false since provided json can have
    #             # control characters like `\n` and `t`
    #             parsed = json.loads(attr, strict=False)
    #         except ValueError:
    #             errorMsg = "Invalid attribute: {}".format(attr)
    #             return RestServer.apiResponse(status=400,
    #                                           body={"error": errorMsg})
    #         # TODO: Temporary fix to escape potential unescaped control
    #         # characters like `\n` and `t`. Get this fixed from the client of
    #         # this api(Catalyst)
    #         op[ENC] = json.dumps(parsed)
    #     request, = client.submit(op)
    #     # Let the request reach the nodes and processing happen
    #     start = time.perf_counter()
    #     elapsed = 0
    #     status = 408
    #     message = {"error": "Timeout"}
    #     while elapsed < longTimeout:
    #         response = client.isRequestSuccessful(request.reqId)
    #         if response is None:
    #             await asyncio.sleep(.2)
    #             elapsed = time.perf_counter() - start
    #         else:
    #             status = 201 if response[0] else 403
    #             message = {'error': response[1]} if not response[0] else \
    #                 request.__dict__
    #             break
    #     return RestServer.apiResponse(status=status, body=message)
