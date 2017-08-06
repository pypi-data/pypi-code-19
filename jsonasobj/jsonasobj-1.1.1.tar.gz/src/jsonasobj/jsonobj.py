# -*- coding: utf-8 -*-
# Copyright (c) 2017, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#     Neither the name of the Mayo Clinic nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
import json
from typing import Union, List, Dict, Tuple
from urllib import request
from urllib.request import Request, urlopen

from .extendednamespace import ExtendedNamespace

# Possible types in the JsonObj representation
JsonObjTypes = Union["JsonObj", List["JsonObjTypes"], str, bool, int, float, None]

# Types in the pure JSON representation
JsonTypes = Union[Dict[str, "JsonTypes"], List["JsonTypes"], str, bool, int, float, None]


class JsonObj(ExtendedNamespace):
    """ A namespace/dictionary representation of a JSON object. Any name in a JSON object that is a valid python
    identifier is represented as a first-class member of the objects.  JSON identifiers that begin with "_" are
    disallowed in this implementation.
    """
    def __init__(self, **kwargs):
        """ Construct a JsonObj from set of keyword/value pairs
        :param kwargs: keyword/value pairs
        """
        ExtendedNamespace.__init__(self, **kwargs)

    def _get(self, item: str, default: JsonObjTypes=None) -> JsonObjTypes:
        return self[item] if item in self else default

    def _default(self, obj):
        """ a function that returns a serializable version of obj or raises TypeError
        :param obj:
        :return: Serialized version of obj
        """
        return obj.__dict__ if isinstance(obj, JsonObj) else json.JSONDecoder().decode(obj)

    def _as_json_obj(self) -> JsonTypes:
        """ Return jsonObj as pure json
        :return: Pure json image
        """
        return json.loads(self._as_json_dumps())

    def _setdefault(self, k: str, value: Union[Dict, JsonTypes]) -> JsonObjTypes:
        if k not in self:
            self[k] = JsonObj(**value) if isinstance(value, dict) else value
        return self[k]

    def _items(self) -> List[Tuple[str, JsonObjTypes]]:
        """ Same as dict items() except that the values are JsonObjs instead of vanilla dictionaries
        :return:
        """
        return [(k, self[k]) for k in self.__dict__.keys()]

    @property
    def _as_json(self, **kwargs) -> JsonTypes:
        """ Convert a JsonObj into straight json
        :param kwargs: json.dumps arguments
        :return: JSON formatted str
        """
        return json.dumps(self, default=self._default, **kwargs)

    def _as_json_dumps(self, indent: str='   ', **kwargs) -> str:
        """ Convert to a stringified json object.  This is the same as _as_json with the exception that it isn't
        a property, meaning that we can actually pass arguments...
        :param indent: indent argument to dumps
        :param kwargs: other arguments for dumps
        :return: JSON formatted string
        """
        return json.dumps(self, default=self._default, indent=indent, **kwargs)

    @staticmethod
    def __as_list(value: List[JsonObjTypes]) -> List[JsonTypes]:
        """ Return a json array as a list
        :param value: array
        :return: array with JsonObj instances removed
        """
        return [e._as_dict if isinstance(e, JsonObj) else e for e in value]

    @property
    def _as_dict(self) -> Dict[str, JsonTypes]:
        """ Convert a JsonObj into a straight dictionary
        :return: dictionary that cooresponds to the json object
        """
        return {k: v._as_dict if isinstance(v, JsonObj) else
                   self.__as_list(v) if isinstance(v, list) else
                   v for k, v in self.__dict__.items()}


def loads(s: str, **kwargs) -> JsonObj:
    """ Convert a json_str into a JsonObj
    :param s: a str instance containing a JSON document
    :param kwargs: arguments see: json.load for details
    :return: JsonObj representing the json string
    """
    return json.loads(s, object_hook=lambda pairs: JsonObj(**pairs), **kwargs)


def load(source, **kwargs) -> JsonObj:
    """ Deserialize a JSON source.
    :param source: a URI, File name or a .read()-supporting file-like object containing a JSON document
    :param kwargs: arguments. see: json.load for details
    :return: JsonObj representing fp
    """
    if isinstance(source, str):
        if '://' in source:
            req = Request(source)
            req.add_header("Accept", "application/json, text/json;q=0.9")
            with urlopen(req) as response:
                jsons = response.read()
        else:
            with open(source) as f:
                jsons = f.read()
    elif hasattr(source, "read"):
        jsons = source.read()
    else:
        raise TypeError("Unexpected type {} for source {}".format(type(source), source))

    return loads(jsons, **kwargs)
