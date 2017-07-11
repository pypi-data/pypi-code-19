from typing import TYPE_CHECKING

import arrow
import requests

from pyEchosign.utils.endpoints import GET_LIBRARY_DOCUMENT, GET_LIBRARY_DOCUMENTS, DELETE_LIBRARY_DOCUMENT
from pyEchosign.utils.request_parameters import get_headers
from pyEchosign.utils.handle_response import check_error

if TYPE_CHECKING:
    from .account import EchosignAccount


class LibraryDocument(object):
    """
    Represents a Library Document in Echosign. When pulling all Library Documents, only the echosign_id, template_type,
    modified_date, name, and scope are available. Accessing all other attributes results in an HTTP request to pull the
    full document information.

    Attributes:
        account (EchosignAccount): An instance of :class:`EchosignAccount <pyEchosign.classes.account.EchosignAccount>`.
         All Agreement actions will be conducted under this account.
        echosign_id (str): The ID for this document in Echosign
        document (bool): If this LibraryDocument is a document in Echosign
        form_field_layer (bool): If this LibraryDocument is a form field layer
        modified_date (datetime): The day on which the LibraryDocument was last modified
        name (str): The name of the LibraryDocument in Echosign
        scope (str): The visibility of this LibraryDocument, either 'PERSONAL', 'SHARED', or 'GLOBAL"
    """

    def __init__(self, account: 'EchosignAccount', echosign_id: str, template_type: list, name: str, modified_date: str, scope: str):
        self.account = account
        self.echosign_id = echosign_id
        if 'DOCUMENT' in template_type:
            self.document = True
        if 'FORM_FIELD_LAYER' in template_type:
            self.form_field_layer = True
        self.name = name
        date = arrow.get(modified_date)
        self.modified_date = date.datetime
        self.scope = scope

    fully_retrieved = False
    document = False
    form_field_layer = False

    PERSONAL = 'PERSONAL'
    SHARED = 'SHARED'
    GLOBAL = 'GLOBAL'
    scope = None

    def retrieve_complete_document(self):
        """ Retrieves the remaining data for the LibraryDocument, such as locale, status, and security options. """
        url = self.account.api_access_point + GET_LIBRARY_DOCUMENT.format(self.echosign_id)
        headers = get_headers(self.account.access_token)
        r = requests.get(url, headers=headers)

        check_error(r)

        response_data = r.json()
        self._locale = response_data.get('locale')
        self.fully_retrieved = True

    def delete(self):
        """ Deletes the LibraryDocument from Echosign. It will not be visible on the Manage page. """
        url = self.account.api_access_point + DELETE_LIBRARY_DOCUMENT.format(self.echosign_id)
        headers = get_headers(self.account.access_token)
        r = requests.delete(url, headers=headers)
        check_error(r)
    
    # The following are only available after retrieving the LibraryDocument specifically
    _events = None
    _latest_version_id = None
    _locale = None
    _participants = None
    _status = None
    _message = None
    _security_options = None

    @property
    def locale(self):
        if not self.fully_retrieved:
            self.retrieve_complete_document()
        return self._locale


class LibraryDocumentsEndpoint(object):
    def __init__(self, account):
        self.account = account

    def get_library_documents(self):
        url = self.account.api_access_point + GET_LIBRARY_DOCUMENTS
        headers = get_headers(self.account.access_token)
        r = requests.get(url, headers=headers)
        response_data = r.json()
        response_data = response_data.get('libraryDocumentList')
        return_data = []

        for document in response_data:
            echosign_id = document.get('libraryDocumentId')
            template_type = document.get('libraryTemplateTypes')
            modified_date = document.get('modifiedDate')
            name = document.get('name')
            scope = document.get('scope')
            library_document = LibraryDocument(self.account, echosign_id, template_type, name, modified_date, scope)
            return_data.append(library_document)

        return return_data
