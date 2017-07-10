# -*- coding: utf-8 -*-

"""
Open Exchange Rates API for Python
"""

import requests


class OXRClient(object):
    default_api = None

    def __init__(self,
                 app_id,
                 api_base="https://openexchangerates.org/api/"):
        self.api_base = api_base.rstrip("/")
        self.app_id = app_id
        self.session = requests.Session()

    @classmethod
    def get_api_client(cls, api=None):
        if api is None:
            return cls.default_api
        return api

    @classmethod
    def get_currencies(cls, api=None):
        """
        Get a JSON list of all currency symbols available from the Open
        Exchange Rates API, along with their full names.
        ref. https://oxr.readme.io/docs/currencies-json
        """
        return cls.get_api_client(api).__request("currencies.json")

    @classmethod
    def get_latest(cls,
                   base=None,
                   symbols=None,
                   api=None
                   ):
        """
        Get latest data.
        ref. https://oxr.readme.io/docs/latest-json
        """
        return cls.get_api_client(api).__get_exchange_rates("latest.json", base, symbols)

    @classmethod
    def get_historical(cls,
                       date,
                       base=None,
                       symbols=None,
                       api=None):
        """
        Get daily historical data
        ref. https://oxr.readme.io/docs/historical-json
        """
        endpoint = "historical/" + date + ".json"
        return cls.get_api_client(api).__get_exchange_rates(endpoint, base, symbols)

    @classmethod
    def get_time_series(cls,
                        start,
                        end,
                        base=None,
                        symbols=None,
                        api=None):
        """
        Get time-series data.
        ref. https://oxr.readme.io/docs/time-series-json
        """
        payload = {"start": start, "end": end}
        return cls.get_api_client(api).__get_exchange_rates("time-series.json",
                                                            base,
                                                            symbols,
                                                            payload)

    @classmethod
    def convert(cls,
                value,
                from_symbol,
                to_symbol,
                api=None
                ):
        """
        Convert any money value from one currency to another at the latest
        API rates.
        ref. https://oxr.readme.io/docs/convert
        """
        api = cls.get_api_client(api)
        endpoint = "convert/{}/{}/{}".format(value, from_symbol, to_symbol)
        payload = {"app_id": api.app_id}
        return api.__request(endpoint, payload)

    def __request(self, endpoint, payload=None):
        url = self.api_base + "/" + endpoint
        request = requests.Request("GET", url, params=payload)
        prepared = request.prepare()

        response = self.session.send(prepared)
        json = response.json()
        if json is None:
            raise OXRDecodeError(request, response)

        if response.status_code != requests.codes.ok:
            if json["message"] == "invalid_base":
                raise OXRInvalidBaseError(request, response)
            elif json["message"] == "invalid_app_id":
                raise OXRInvalidAppIdError(request, response)
            elif json["message"] == "missing_app_id":
                raise OXRMissingAppIdError(request, response)
            elif json["message"] == "not_allowed":
                raise OXRNotAllowedError(request, response)
            raise OXRStatusError(request, response, json["message"], json["description"])
        return json

    def __get_exchange_rates(self, endpoint, base, symbols, payload=None):
        if payload is None:
            payload = dict()
        payload["app_id"] = self.app_id
        if base is not None:
            payload["base"] = base
        if isinstance(symbols, list) or isinstance(symbols, tuple):
            symbols = ",".join(symbols)
        if symbols is not None:
            payload["symbols"] = symbols
        return self.__request(endpoint, payload)


class OXRError(Exception):
    """Open Exchange Rates Error"""

    def __init__(self, req, resp):
        super(OXRError, self).__init__()
        self.request = req
        self.response = resp


class OXRInvalidBaseError(OXRError):
    """Requested exchange rates for bad base"""

    def __str__(self):
        return "Invalid base"


class OXRNotAllowedError(OXRError):
    """Doesn’t have permission to access requested route/feature"""

    def __str__(self):
        return "Doesn’t have permission to access requested route/feature"


class OXRInvalidAppIdError(OXRError):
    """Requested exchange rates with invalid app id"""

    def __str__(self):
        return "Invalid App ID"


class OXRMissingAppIdError(OXRError):
    """Requested exchange rates without app id"""

    def __str__(self):
        return "Missing App ID"


class OXRStatusError(OXRError):
    """API status code error"""

    def __init__(self, req, resp, message, description):
        super(OXRError, self).__init__(req, resp)

        self.message = message
        self.description = description

    def __str__(self):
        return self.description


class OXRDecodeError(OXRError):
    """JSON decode error"""
    pass


def init(app_id):
    OXRClient.default_api = OXRClient(app_id=app_id)
