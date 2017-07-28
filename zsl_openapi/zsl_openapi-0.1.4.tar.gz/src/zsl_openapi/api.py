from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import *  # NOQA
from typing import Dict  # NOQA
from typing import List  # NOQA

from werkzeug.datastructures import ImmutableDict
from werkzeug.datastructures import ImmutableList


class ApiExternalDocs:
    def __init__(self):
        self.description = None  # type: str
        self.url = None  # type: str


class ApiTag:
    def __init__(self):
        self.name = None  # type: str
        self.description = None  # type: str
        self.external_docs = ApiExternalDocs()


class ApiLicense:
    def __init__(self):
        self.name = None  # type:str
        self.url = None  # type:str


class ApiContact:
    def __init__(self):
        self.email = None  # type:str


class ApiDescriptionInfo:
    def __init__(self):
        self.description = None  # type: str
        self.version = None  # type: str
        self.title = None  # type: str
        self.terms_of_service = None  # type: str
        self.contact = ApiContact()
        self.license = ApiLicense()


class ApiArrayProperty:
    def __init__(self):
        self.type = None  # type: str
        self.ref = None  # type: str


class ApiModelProperty:
    def __init__(self):
        self.name = None  # type: str
        self.type = None  # type: str
        self.format = None  # type: str
        self.items = ApiArrayProperty()


class ApiModelDefinition:
    def __init__(self):
        self.name = None  # type: str
        self.type = None  # type: str
        self._properties = {}  # type: Dict[str, ApiModelProperty]

    @property
    def properties(self):
        # type: ()->Dict[str, ApiModelProperty]
        return ImmutableDict(self._properties)

    def add_property(self, model_property):
        # type: (ApiModelProperty)->None
        self._properties[model_property.name] = model_property


class ApiDescription:
    def __init__(self):
        self.info = ApiDescriptionInfo()
        self.external_docs = ApiExternalDocs()
        self._tags = []  # type: List[ApiTag]
        self._definitions = {}  # type: Dict[str, ApiModelDefinition]

    @property
    def tags(self):
        # type: ()->List[ApiTag]
        return ImmutableList(self._tags)

    @property
    def definitions(self):
        # type: ()->Dict[str, ApiModelDefinition]
        return ImmutableDict(self._definitions)

    def add_model_definition(self, model_definition):
        # type: (ApiModelDefinition)->None
        self._definitions[model_definition.name] = model_definition

    def add_tag(self, tag):
        # type: (ApiTag)->None
        self._tags.append(tag)
