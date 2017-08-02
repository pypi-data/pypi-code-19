# Helpers for implementing anvil.server.
# Used in uplink, downlink and pypy-sandbox.

import anvil
import traceback
import numbers
import sys
import re
import json

_do_call = None

string_type = str if sys.version_info >= (3,) else basestring
long_type = int if sys.version_info >= (3,) else long

class LiveObjectProxy(anvil.LiveObject):

    def __init__(self,spec):
        for k in ["itemCache", "iterItems"]:
            if spec.get(k, {}) is None:
                del spec[k]
        anvil.LiveObject.__init__(self, spec)

    def __getattr__(self, item):
        if item in self._spec["methods"]:
            def item_fn(*args, **kwargs):
                lo_call = dict(self._spec)
                lo_call["method"] = item
                return _do_call(args, kwargs, lo_call=lo_call)

            return item_fn
        else:
            raise AttributeError(item)

    def __getitem__(self, item):
        if item in self._spec.get("itemCache", {}):
            return self._spec["itemCache"][item]

        getitem = self.__getattr__("__getitem__")

        try:
            return getitem(item)
        except AnvilWrappedError as e:
            raise _deserialise_exception(e.error_obj)

    def __setitem__(self, key, value):
        if key in self._spec.get("itemCache", {}):
            del self._spec["itemCache"][key]

        setitem = self.__getattr__("__setitem__")
        try:
            r = setitem(key, value)
        except AnvilWrappedError as e:
            raise _deserialise_exception(e.error_obj)

        if "itemCache" in self._spec and (isinstance(value, str) or isinstance(value, numbers.Number) or isinstance(value, bool) or value is None):
            self._spec["itemCache"][key] = value

        return r

    class Iter:
        def __init__(self, live_object):
            self._lo_call = dict(live_object._spec)
            self._lo_call["method"] = "__anvil_iter_page__";

            i = live_object._spec.get("iterItems", {})
            self._idx = 0
            self._items = i.get("items", None)
            self._next_page = i.get("nextPage", None)

        def _fetch_state(self):
            r = _do_call([self._next_page], {}, lo_call=self._lo_call)
            self._items = r["items"]
            self._next_page = r.get("nextPage", None)
            self._idx = 0

        def __iter__(self):
            return self

        def next(self):
            if self._items is None:
                try:
                    self._fetch_state()
                except AnvilWrappedError as e:
                    raise _deserialise_exception(e.error_obj)

            if self._idx < len(self._items):
                r = self._items[self._idx]
                self._idx += 1
                return r

            if self._next_page is None:
                raise StopIteration

            self._items = None
            return self.next()

        def __next__(self):
            return self.next()

    def __iter__(self):
        if "__anvil_iter_page__" in self._spec["methods"]:
            return LiveObjectProxy.Iter(self)
        else:
            raise Exception("Not iterable: <LiveObject: %s>" % self._spec.get("backend", "INVALID"))

    def __len__(self):
        if "__len__" in self._spec["methods"]:
            return int(self.__getattr__("__len__")())
        else:
            l = 0
            for _ in self.__iter__():
                l += 1
            return l


class LazyMedia(anvil.Media):
    def __init__(self, spec):
        if isinstance(spec,LazyMedia):
            spec = spec._spec
        self._spec = spec
        self._details = None
        self._fetched = None

    def _fetch(self):
        if self._details is None:
            import anvil.server
            self._fetched = anvil.server.call("fetch_lazy_media", self._spec)
        return self._fetched

    def _get(self, key, attr=None):
        if attr is None:
            attr = key
        return self._spec[key] if key in self._spec else getattr(self._fetch(), attr)

    def get_name(self):
        try:
            return self._get("name")
        except AnvilWrappedError as e:
            raise _deserialise_exception(e.error_obj)


    def get_content_type(self):
        try:
            return self._get("mime-type", "content_type")
        except AnvilWrappedError as e:
            raise _deserialise_exception(e.error_obj)

    def get_length(self):
        try:
            return self._get("length")
        except AnvilWrappedError as e:
            raise _deserialise_exception(e.error_obj)

    def get_bytes(self):
        try:
            return self._fetch().get_bytes()
        except AnvilWrappedError as e:
            raise _deserialise_exception(e.error_obj)


class AnvilWrappedError(Exception):
    def __init__(self, error_obj):
        self.error_obj = error_obj
        self.message = self.error_obj.get("message", "")
        Exception.__init__(self, self.message)

    def __str__(self):
        eo_type = self.error_obj.get("type")
        if type(self) is AnvilWrappedError and eo_type is not None:
            return str(eo_type) + ": " + repr(self.message)
        return repr(self.message)


_named_exceptions = {}


def _register_exception_type(name, cls):
    _named_exceptions[name] = cls


def _deserialise_exception(error_obj):
    return _named_exceptions.get(error_obj.get("type"), AnvilWrappedError)(error_obj)


class AnvilSerializationError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


def _report_exception(request_id=None):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb = traceback.extract_tb(exc_traceback)

    trace = [(filename.replace("\\","/"), lineno) for (filename, lineno, _, _) in tb]
    trace.reverse()

    # Last element of trace is where we called into user code. Remove it.
    trace.pop()

    if isinstance(exc_value, AnvilWrappedError):
        # First element of trace is where we re-raised the exception. Remove it.
        trace = trace[1:]
        exc_value.error_obj["trace"] = exc_value.error_obj.get("trace", []) + trace
        r = {
            "error": exc_value.error_obj,
            "id": request_id
        }
        return r
    elif isinstance(exc_value, SyntaxError):
        # Remove whole internal trace and replace it with line where error occurred.
        trace=[(exc_value.filename, exc_value.lineno)]
        return {
            "error": {
                "type": "SyntaxError",
                "trace": trace,
                "message": str(exc_value)
            },
            "id": request_id
        }
    elif isinstance(exc_value, AnvilSerializationError):
        return {
            "error": {
                "type": "AnvilSerializationError",
                "trace": [],
                "message": exc_value.message,
            },
            "id": request_id
        }
    else:
        return {
            "error": {
                "type": str(exc_type.__name__),
                "trace": trace,
                "message": str(exc_value),
            },
            "id": request_id
        }

def reconstruct_val(v, reconstruct_data_media=None):

    for t in v["type"]:
        if t == "DataMedia":
            if reconstruct_data_media is None:
                raise Exception("No data media deserialiser provided. Cannot reconstruct.")
            return reconstruct_data_media(v)
        elif t == "LazyMedia":
            return LazyMedia(v)
        elif t == "LiveObject":
            return reconstruct_live_object(v)
        elif t == "Date":
            return parsedate(v["value"]) if v["value"] else None
        elif t == "DateTime":
            return parsedatetime(v["value"]) if v["value"] else None
        elif t == "Long":
            return long_type(v["value"])
        elif t == "Primitive":
            return v["value"]

    raise Exception("Server module cannot accept an object of type '%s'" % v["type"][0])



def reconstruct_live_object(d):

    reconstructed_item_cache = {}
    for k,v in d.get("itemCache", {}).items():
        reconstructed_item_cache[k] = reconstruct_val(v)
    d["itemCache"] = reconstructed_item_cache

    if d.get("iterItems"):
        reconstructed_iteritems = []
        for i in d["iterItems"]["items"]:
            reconstructed_iteritems.append(reconstruct_val(i))
        d["iterItems"]["items"] = reconstructed_iteritems

    return LiveObjectProxy(d)


def serialise_val(v):
    import datetime
    if isinstance(v, long_type) and not isinstance(v, bool):
        return {
            "type": ["Long"],
            "value": str(v)
        }
    elif isinstance(v, (numbers.Number, bool, string_type)) or v is None:
        return {
            "type": ["Primitive"],
            "value": v
        }
    elif isinstance(v, anvil.LiveObject):
        return serialise_live_object(v)
    elif isinstance(v, datetime.datetime):
        s = "%04d-%02d-%02d %02d:%02d:%02d.%d" % (v.year, v.month, v.day, v.hour, v.minute, v.second, v.microsecond)

        if v.tzinfo is not None:
            offset = v.tzinfo.utcoffset(v).total_seconds()
        else:
            offset = 0

        sign = "+" if offset >= 0 else "-"
        z = "%s%02d%02d" % (sign, abs(int(offset/3600)), int((offset % 3600)/60))

        return {
            "type": ["DateTime"],
            "value": s + z
        }
    elif isinstance(v, datetime.date):
        s = "%04d-%02d-%02d" % (v.year, v.month, v.day)
        return {
            "type": ["Date"],
            "value": s
        }


def serialise_live_object(obj):
    obj = obj._spec.copy()
    obj["type"] = ["LiveObject"]

    serialised_item_cache = {}
    for k,v in obj.get("itemCache", {}).items():
        serialised_item_cache[k] = serialise_val(v)
    obj["itemCache"] = serialised_item_cache

    if obj.get("iterItems"):
        serialised_iteritems = []
        for i in obj["iterItems"]["items"]:
            serialised_iteritems.append(serialise_val(i))
        obj["iterItems"]["items"] = serialised_iteritems

    return obj


def fill_out_media(json, handle_media_fn):
    obj_descr = []
    path = []
    import datetime

    def do_fom(_json):
        if isinstance(_json, dict):
            _json = dict(_json)
            for i in _json:
                path.append(i)
                _json[i] = do_fom(_json[i])
                path.pop()
        elif isinstance(_json, list) or isinstance(_json, tuple):
            _json = list(_json)
            for i in range(len(_json)):
                path.append(i)
                _json[i] = do_fom(_json[i])
                path.pop()
        elif isinstance(_json, LazyMedia):
            d = dict(_json._spec)
            d["path"] = list(path)
            obj_descr.append(d)
            _json = None
        elif isinstance(_json, anvil.Media):
            extra = handle_media_fn(_json)
            d = {"type": ["DataMedia"], "path": list(path), "mime-type": _json.content_type, "name": _json.name}
            if extra is not None:
                d.update(extra)
            obj_descr.append(d)
            _json = None
        elif isinstance(_json, anvil.LiveObject):
            #print "Serialising LiveObject: " + repr(_json._spec) + " at " + repr(path)
            serialised_liveobject = serialise_live_object(_json)
            serialised_liveobject["path"] = list(path)
            obj_descr.append(serialised_liveobject)
            _json = None
        elif isinstance(_json, (datetime.date, datetime.datetime)) or \
                (isinstance(_json, long_type) and (_json > 2147483647 or _json < -2147483647)):
            serialised_val = serialise_val(_json)
            serialised_val["path"] = list(path)
            obj_descr.append(serialised_val)
            _json = None

        return _json

    json = do_fom(json)
    json["objects"] = obj_descr
    return json


def simple_strpdate(s):
    import datetime
    return datetime.date(int(s[0:4]), int(s[5:7]), int(s[8:10]))


def simple_strpdatetime(s):
    import datetime
    return datetime.datetime(int(s[0:4]), int(s[5:7]), int(s[8:10]), int(s[11:13]), int(s[14:16]), int(s[17:19]), int(s[20:26])) # datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")

def parsedate(s):
    return simple_strpdate(s)


def parsedatetime(s):

    has_tz = len(s) > 5 and \
             (s[-5] == "-" or s[-5] == "+") and \
             48 <= ord(s[-4]) <= 57 and \
             48 <= ord(s[-3]) <= 57 and \
             48 <= ord(s[-2]) <= 57 and \
             48 <= ord(s[-1]) <= 57

    if not has_tz:
        # Parse a naive datetime
        return simple_strpdatetime(s)

    # Timezone present. First parse without it
    d = simple_strpdatetime(s[:-5])

    # Now construct a tzoffset
    hours = int(s[-5:-2])
    minutes = int(s[-5] + s[-2:])
    total_minutes = hours*60+minutes

    # Cannot import earlier - circular dependency!
    import anvil.tz

    return d.replace(tzinfo=anvil.tz.tzoffset(minutes=total_minutes))


def _reconstruct_objects(json, reconstruct_data_media):
    def set_in_path(obj, path, payload):
        last_obj = None
        key = None
        for k in path:
            last_obj = obj
            key = k
            obj = obj[k]

        if last_obj is not None:
            last_obj[key] = payload

    if "objects" in json:
        for d in json["objects"]:
            reconstructed = reconstruct_val(d, reconstruct_data_media)
            set_in_path(json, d["path"], reconstructed)

        del json["objects"]

    return json

on_register = None # optional
registrations = {}

class HttpRequest:
    pass
api_request = HttpRequest()

class HttpResponse():

    def __init__(self, status=200, body=""):
        self.status = status
        self.body = body
        self.headers = {}

def http_endpoint(path, require_credentials=False, authenticate_users=False, authenticate_user=False):
    def decorator(fn):
        path_parts = []
        def register_path_part(s):
            path_parts.append(s.group(1))
            return "([^/]*)"

        path_regex = re.sub(":([^/]*)", register_path_part, path)

        def wrapped_fn(method, path, query_params, form_params, origin, headers, remote_address, body, username, password, **more_kwargs):

            api_request.user = None
            if authenticate_users or authenticate_user:
                import anvil.users
                try:
                    api_request.user = anvil.users.login_with_email(username, password)
                except (anvil.users.AuthenticationFailed, anvil.users.AccountIsNotEnabled) as e:
                    return {"status": 401,
                            "body": "Unauthorized",
                            "headers": {"WWW-Authenticate": "Basic realm=\"Anvil App API\""}}
            elif require_credentials:
                if username is None or password is None:
                    return {"status": 401,
                            "body": "Unauthorized",
                            "headers": {"WWW-Authenticate": "Basic realm=\"Anvil App API\""}}

            api_request.path = path
            api_request.method = method
            api_request.query_params = query_params
            api_request.form_params = form_params
            api_request.origin = origin
            api_request.headers = headers
            api_request.remote_address = remote_address
            api_request.body = body
            api_request.username = username
            api_request.password = password

            if body is not None and headers.get("content-type", None) == "application/json":
                api_request.body_json = json.loads(api_request.body.get_bytes())
            else:
                api_request.body_json = None

            
            # Path takes precedence over query params. Query params take precedence over form params.
            kwargs = dict(form_params)
            kwargs.update(query_params)
            match = re.match(path_regex, path)
            for i,m in enumerate(match.groups()):
                kwargs[path_parts[i]] = m

            response = fn(**kwargs)

            if isinstance(response, HttpResponse):
                return {"status":  response.status,
                        "body":    response.body,
                        "headers": response.headers}
            else:
                return {"status":  200,
                        "body":    response}


        registrations["http:" + path_regex] = wrapped_fn

        if on_register is not None:
            on_register("http:" + path_regex, False)

        return fn
    return decorator
