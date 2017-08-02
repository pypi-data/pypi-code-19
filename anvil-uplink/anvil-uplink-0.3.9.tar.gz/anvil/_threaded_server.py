# Helpers for implementing anvil.server on a threaded Real Python process.
# Used in uplink and downlink, but not in pypy-sandbox.

import threading, random, string, json, re, sys

from . import  _serialise, _server
from ._server import LazyMedia, registrations

console_output = sys.stdout

class HttpRequest(threading.local):
    pass

_server.api_request = HttpRequest()

def _gen_id():
    return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10))


# Overwrite with functions from context
send_reqresp = None


class LocalCallInfo(threading.local):
    def __init__(self):
        self.stack_id = None
        self.session = None

    def __getitem__(self, item):
        return self.session.__getitem__(item)

    def __setitem__(self, key, value):
        return self.session.__setitem__(key, value)

    def __delitem__(self, key):
        del self.session[key]

    def get(self, key, default=None):
        return self.session.get(key, default)

    def __iter__(self):
        return self.session.__iter__()


call_info = LocalCallInfo()
call_responses = {}
waiting_for_calls = threading.Condition()

backends = {}


class IncomingRequest(_serialise.IncomingReqResp):
    def execute(self):
        def make_call():
            call_info.stack_id = self.json.get('call-stack-id', None)
            call_info.session = self.json.get('sessionData', None)
            try:
                if 'liveObjectCall' in self.json:
                    loc = self.json['liveObjectCall']
                    spec = dict(loc)

                    if self.json["id"].startswith("server-"):
                        spec["source"] = "server"
                    elif self.json["id"].startswith("client-"):
                        spec["source"] = "client"
                    else:
                        spec["source"] = "UNKNOWN"

                    del spec["method"]
                    backend = loc['backend']
                    if backend not in backends:
                        raise Exception("No such LiveObject backend: " + repr(backend))
                    inst = backends[backend](spec)
                    method = getattr(inst, loc['method'])
                    response = method(*self.json['args'], **self.json['kwargs'])
                else:
                    command = self.json['command']
                    for reg in registrations:
                        m = re.match(reg, command)
                        if m and len(m.group(0)) == len(command):
                            response = registrations[reg](*self.json["args"], **self.json["kwargs"])
                            break
                    else:
                        raise Exception('No server function matching "%s" has been registered' % command)


                try:
                    json.dumps(call_info.session)
                except:
                    raise Exception("anvil.server.session may only contain strings, numbers, lists and dicts")

                try:
                    send_reqresp({"id": self.json["id"], "response": response, "sessionData": call_info.session})
                except _server.AnvilSerializationError as e:
                    raise _server.AnvilSerializationError("Cannot serialize return value from function. " + e.message)
            except:
                e = _server._report_exception(self.json["id"])
                try:
                    send_reqresp(e)
                except:
                    trace = "\ncalled from ".join(["%s:%s" % (t[0], t[1]) for t in e["error"]["trace"]])
                    console_output.write(("Failed to report exception: %s: %s\nat %s\n" % (e["error"]["type"], e["error"]["message"], trace)).encode("utf-8"))
                    console_output.flush()
            finally:
                self.complete()

        threading.Thread(target=make_call).start()

    def complete(self):
        pass


class IncomingResponse(_serialise.IncomingReqResp):
    def execute(self):
        id = self.json['id']
        if id in call_responses:
            call_responses[id] = self.json
            with waiting_for_calls:
                waiting_for_calls.notifyAll()
        else:
            print("Got a response for an unknown ID: " + repr(self.json))


def kill_outstanding_requests(msg):
    for k in call_responses.keys():
        if call_responses[k] is None:
            call_responses[k] = {'error': msg}

    with waiting_for_calls:
        waiting_for_calls.notifyAll()


# can be used as a decorator too
def register(fn, name=None):
    if isinstance(fn, str):
        # Someone's using the old syntax. Our bad.
        (fn, name) = (name, fn)

    if name is None:
        name = fn.__name__

    registrations[name] = fn

    if _server.on_register is not None:
        _server.on_register(name, False)

    def reregister(new_f):
        registrations[name] = new_f
        new_f._anvil_reregister = reregister

    fn._anvil_reregister = reregister

    return fn


callable = register


def register_live_object_backend(cls):

    name = "uplink." + cls.__name__
    backends[name] = cls

    if _server.on_register is not None:
        _server.on_register(name, True)

    return cls


live_object_backend = register_live_object_backend


# A parameterised decorator
def callable_as(name):
    return lambda f: register(f, name)


def do_call(args, kwargs, fn_name=None, lo_call=None): # Yes, I do mean args and kwargs without *s
    id = _gen_id()

    call_responses[id] = None

    with waiting_for_calls:
        #print("Call stack ID = " + repr(_call_info.stack_id))
        if call_info.stack_id is None:
            call_info.stack_id = "outbound-" + _gen_id()
        req = {'type': 'CALL', 'id': id, 'args': args, 'kwargs': kwargs,
               'call-stack-id': call_info.stack_id}

        if fn_name:
            req["command"] = fn_name
        elif lo_call:
            req["liveObjectCall"] = lo_call
        else:
            raise Exception("Expected one of fn_name or lo_call")

        try:
            send_reqresp(req)
        except _server.AnvilSerializationError as e:
            raise _server.AnvilSerializationError("Cannot serialize arguments to function. " + e.message)

        while call_responses[id] is None:
            waiting_for_calls.wait()

    r = call_responses.pop(id)

    if 'response' in r:
        return r['response']
    if 'error' in r:
        raise _server._deserialise_exception(r["error"])
    else:
        raise Exception("Bogus response from server: " + repr(r))
