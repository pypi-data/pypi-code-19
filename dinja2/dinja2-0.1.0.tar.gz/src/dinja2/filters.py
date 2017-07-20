# coding=utf-8
import logging
from collections import OrderedDict
from urllib.parse import parse_qsl, urlencode


def do_append_get(url, **kwargs):
    logging.debug("path: %s" % url)
    if "?" in url:
        path, qs = url.split("?")
        query_params = OrderedDict(parse_qsl(qs))
        logging.debug("query_params: %s" % query_params)
        query_params.update(kwargs)
        logging.debug("query_params: %s" % query_params)
        return path + "?" + urlencode(query_params, doseq=True)
    else:
        suffix = urlencode(kwargs)
        return url + "?" + suffix


def do_class_name(var):
    return var.__class__.__name__
