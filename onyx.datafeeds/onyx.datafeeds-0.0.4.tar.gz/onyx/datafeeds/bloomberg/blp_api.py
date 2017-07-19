###############################################################################
#
#   Copyright: (c) 2015 Carlo Sbraccia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###############################################################################

from onyx.core import Date, Curve, HlocvCurve, GCurve

from ..exceptions import SecurityError, FieldError
from ..exceptions import DatafeedError, DatafeedFatal

import datetime
import blpapi

sec_err_fmt = "({0:s}, {1:s}, {2:s})"
fld_err_fmt = "{0:s}, {1:s}, {2:s}, {3:s}"

SECURITY_DATA = blpapi.Name("securityData")
SECURITY = blpapi.Name("security")
CATEGORY = blpapi.Name("category")
MESSAGE = blpapi.Name("message")
SEC_ERROR = blpapi.Name("securityError")
FIELD_DATA = blpapi.Name("fieldData")
FIELD_EXCEPTIONS = blpapi.Name("fieldExceptions")
FIELD_ID = blpapi.Name("fieldId")
ERROR_INFO = blpapi.Name("errorInfo")

bbg_datatypes = blpapi.datatype.DataType()

VANILLA_TYPES = {
    bbg_datatypes.BOOL,
    bbg_datatypes.CHAR,
    bbg_datatypes.BYTE,
    bbg_datatypes.INT32,
    bbg_datatypes.INT64,
    bbg_datatypes.FLOAT32,
    bbg_datatypes.FLOAT64,
}
bbg_datatypes.VANILLA_TYPES = VANILLA_TYPES


# -----------------------------------------------------------------------------
def get_sequence_value(node):
    """
    Convert an element with DataType Sequence to a list of dictionaries.
    Note this may be a naive implementation as it assumes that bulk data is
    always a table.
    """
    data, cols = [], []
    for i in range(node.numValues()):
        row = node.getValue(i)
        # --- get the ordered cols and assume they are constant
        if i == 0:
            cols = [str(row.getElement(k).name())
                    for k in range(row.numElements())]

        values = []
        for cidx in range(row.numElements()):
            elm = row.getElement(cidx)
            if elm.numValues():
                values.append(get_value(elm))
            else:
                values.append(None)

        data.append(dict(zip(cols, values)))

    return data


# -----------------------------------------------------------------------------
def get_value(ele):
    """
    Convert the specified element as a python value.
    """
    dtype = ele.datatype()
    if dtype in bbg_datatypes.VANILLA_TYPES:
        return ele.getValue()

    elif dtype == bbg_datatypes.STRING:
        return str(ele.getValue())

    elif dtype == bbg_datatypes.DATE:
        v = ele.getValue()
        if v is None:
            return None
        else:
            return Date(year=v.year, month=v.month, day=v.day)

    elif dtype == bbg_datatypes.TIME:
        v = ele.getValue()
        if v is None:
            return None
        else:
            return datetime.time(hour=v.hour, minute=v.minute, second=v.second)

    elif dtype == bbg_datatypes.DATETIME:
        v = ele.getValue()
        if v is None:
            return None
        else:
            return Date(year=v.year, month=v.month, day=v.day,
                        hour=v.hour, minute=v.minute, second=v.second)

    elif dtype == bbg_datatypes.ENUMERATION:
        raise NotImplementedError("ENUMERATION "
                                  "data type not implemented")

    elif dtype == bbg_datatypes.SEQUENCE:
        return get_sequence_value(ele)

    elif dtype == bbg_datatypes.CHOICE:
        raise NotImplementedError("CHOICE data type not implemented")

    else:
        raise NotImplementedError("Unexpected data type {0:s}. "
                                  "Check documentation".format(dtype))


# -----------------------------------------------------------------------------
def test_bbg_data_service():
    session = blpapi.Session()

    try:
        active = session.start()
    except:
        return False

    try:
        active = session.openService("//blp/refdata")
    except:
        return False
    finally:
        session.stop()

    return active


# -----------------------------------------------------------------------------
def process_bdp_message(msg, field_names):
    response = {}

    if not msg.hasElement(SECURITY_DATA):
        raise DatafeedError("unexpected message:\n{0!s}".format(msg))

    securityDataArray = msg.getElement(SECURITY_DATA)

    for securityData in securityDataArray.values():
        security = securityData.getElementAsString(SECURITY)

        if securityData.hasElement(SEC_ERROR):
            error = securityData.getElement(SEC_ERROR)
            cat = error.getElementAsString(CATEGORY)
            msg = error.getElementAsString(MESSAGE)
            raise SecurityError(sec_err_fmt.format(security, cat, msg))

        fieldExceptionArray = securityData.getElement(FIELD_EXCEPTIONS)
        for fieldException in fieldExceptionArray.values():
            errorInfo = fieldException.getElement(ERROR_INFO)
            field = fieldException.getElementAsString(FIELD_ID)
            cat = errorInfo.getElementAsString(CATEGORY)
            msg = errorInfo.getElementAsString(MESSAGE)
            raise FieldError(fld_err_fmt.format(security, field, cat, msg))

        response[security] = {}

        fieldData = securityData.getElement(FIELD_DATA)

        for field_name in field_names:
            if fieldData.hasElement(field_name):
                value = get_value(fieldData.getElement(field_name))
            else:
                value = None

            response[security][field_name] = value

    return response


# -----------------------------------------------------------------------------
def BbgBDP(securities, fields, overrides=None, timeout=500):
    """
    Description:
        Executes a blocking BDP request.
    Inputs:
        securities - one or more valid Bloomberg tickers
        fields     - one or more valid Bloomberg fields
        overrides  - an optional dictionary of overrides (or a tuple
                     of key, value tuples)
        timeout    - timeout interval in milliseconds. A value of zero means
                     wait forever.
    Returns:
        A dictionary or raises TimeoutError if the request times out.
    """
    if isinstance(securities, str):
        securities = [securities]
    if isinstance(fields, str):
        fields = [fields]
    if overrides is None:
        overrides = {}
    elif isinstance(overrides, tuple):
        overrides = dict(overrides)

    # --- look for any date-override and convert it to its correct string
    #     representation
    for k, v in overrides.items():
        if isinstance(v, datetime.datetime):
            overrides[k] = v.strftime("%Y%m%d")

    session = blpapi.Session()

    if not session.start():
        raise DatafeedFatal("failed to start session")

    try:
        if not session.openService("//blp/refdata"):
            raise DatafeedFatal("failed to open '//blp/refdata' service")

        service = session.getService("//blp/refdata")
        request = service.createRequest("ReferenceDataRequest")

        for sec in securities:
            request.append("securities", sec)
        for fld in fields:
            request.append("fields", fld)

        for field, value in overrides.items():
            ovd = request.getElement("overrides").appendElement()
            ovd.setElement("fieldId", field)
            ovd.setElement("value", value)

        cid = blpapi.CorrelationId(1)
        queue = blpapi.EventQueue()
        session.sendRequest(request, correlationId=cid, eventQueue=queue)

        while True:
            ev = queue.nextEvent(timeout)

            # --- request timed out, raise exception
            if ev.eventType() == blpapi.Event.TIMEOUT:
                raise TimeoutError("request timed out "
                                   "after {0!s} milliseconds".format(timeout))

            for msg in ev:
                if cid in msg.correlationIds():
                    response = process_bdp_message(msg, fields)

            # --- response completly received, exit
            if ev.eventType() == blpapi.Event.RESPONSE:
                break

    finally:
        session.stop()

    return response


# -----------------------------------------------------------------------------
def BbgBDH(security, fields, start, end,
           adj=True, overrides=None, timeout=500, **kwds):
    """
    Description:
        Executes a blocking BDH request.
    Inputs:
        secirity  - a valid Bloomberg ticker
        fields    - one or more valid Bloomberg fields. "HLOCV" is a special
                    field type.
        start     - start date
        end       - end date
        adj       - True for dividend/split adjusted data
        overrides - an optional dictionary of overrides (or a tuple
                    of key, value tuples)
        timeout   - timeout interval in milliseconds. A value of zero means
                    wait forever.
    Returns:
        Depending on fields, a Curve or HlocvCurve or GCurve or raises
        TimeoutError if the request times out.
    """
    if fields == "HLOCV":
        fields = ["PX_HIGH", "PX_LOW", "PX_OPEN", "PX_LAST", "VOLUME"]
        is_hlocv = True
    else:
        is_hlocv = False
        fields = [fields] if isinstance(fields, str) else list(fields)

    # --- fildnames is used to iterate over fieldData element
    field_names = ["date"] + fields

    if overrides is None:
        overrides = {}
    elif isinstance(overrides, tuple):
        overrides = dict(overrides)

    # --- look for any date-override and convert it to its correct string
    #     representation
    for k, v in overrides.items():
        if isinstance(v, datetime.datetime):
            overrides[k] = v.strftime("%Y%m%d")

    session = blpapi.Session()

    if not session.start():
        raise DatafeedFatal("failed to start session")

    try:
        if not session.openService("//blp/refdata"):
            raise DatafeedFatal("failed to open '//blp/refdata' service")

        service = session.getService("//blp/refdata")
        request = service.createRequest("HistoricalDataRequest")

        request.append("securities", security)
        for fld in fields:
            request.append("fields", fld)

        request.set("periodicitySelection", "DAILY")
        request.set("startDate", start.strftime("%Y%m%d"))
        request.set("endDate", end.strftime("%Y%m%d"))
        request.set("adjustmentNormal", adj)
        request.set("adjustmentAbnormal", adj)
        request.set("adjustmentSplit", adj)

        cid = blpapi.CorrelationId(1)
        queue = blpapi.EventQueue()
        session.sendRequest(request, correlationId=cid, eventQueue=queue)

        data = []
        while True:
            ev = queue.nextEvent(timeout)

            # --- request timed out, raise exception
            if ev.eventType() == blpapi.Event.TIMEOUT:
                raise TimeoutError("request timed out "
                                   "after {0!s} milliseconds".format(timeout))

            for msg in ev:
                if not msg.hasElement(SECURITY_DATA):
                    continue

                securityData = msg.getElement(SECURITY_DATA)

                if securityData.hasElement(SEC_ERROR):
                    error = securityData.getElement(SEC_ERROR)
                    cat = error.getElementAsString(CATEGORY)
                    msg = error.getElementAsString(MESSAGE)
                    raise SecurityError(sec_err_fmt.format(security, cat, msg))

                fieldExceptionArray = securityData.getElement(FIELD_EXCEPTIONS)
                for fieldException in fieldExceptionArray.values():
                    errorInfo = fieldException.getElement(ERROR_INFO)
                    field = fieldException.getElementAsString(FIELD_ID)
                    cat = errorInfo.getElementAsString(CATEGORY)
                    msg = errorInfo.getElementAsString(MESSAGE)
                    raise FieldError(fld_err_fmt.format(security,
                                                        field, cat, msg))

                fieldDataArray = securityData.getElement(FIELD_DATA)
                for fieldData in fieldDataArray.values():
                    knot = [None, {}]
                    for field_name in field_names:
                        if fieldData.hasElement(field_name):
                            value = get_value(fieldData.getElement(field_name))
                        else:
                            value = None

                        if field_name == "date":
                            knot[0] = value
                        else:
                            knot[1][field_name] = value

                    data.append(knot)

            # --- response completly received, so we could exit
            if ev.eventType() == blpapi.Event.RESPONSE:
                break

    finally:
        session.stop()

    if is_hlocv:
        if len(data):
            # --- remove knots without a close value (should be extremely rare)
            knots = [(d, [v[fld] for fld in fields])
                     for d, v in data if v["PX_LAST"] is not None]
            return HlocvCurve([d for d, v in knots], [v for d, v in knots])

        else:
            return HlocvCurve()

    elif len(fields) == 1:
        if len(data):
            fld = fields[0]
            try:
                float(data[0][1][fld])
            except ValueError:
                return data
            else:
                knots = [(d, v[fld]) for d, v in data]
                return Curve([d for d, v in knots], [v for d, v in knots])
        else:
            return Curve()
    else:
        return GCurve([d for d, v in data], [v for d, v in data])
