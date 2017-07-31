import logging
import requests

def create_document_set(server_url, api_token, title, metadata_schema={'version':1,'fields':[]}, logger=None):
    """Create a DocumentSet on the Overview server.

    :param str server_url: Website URL. For example:
        ``https://www.overviewdocs.com``
    :param str api_token: String from
        https://www.overviewdocs.com/api-tokens (NOT an API token for a
        particular document set).
    :param str title: Title to give the new document set.
    :param dict metadata_schema: Initial metadata schema for the document set.
    :param Logger logger: Where to log activities.
    """
    if logger is None:
        logger = logging.getLogger('{}.create_document_set'.format(__name__))

    url = '{}/api/v1/document-sets'.format(server_url)
    logger.debug('POST %s', url)
    r = requests.request('POST', url,
        headers={
            'Accept': 'application/json',
            'X-Requested-With': 'overview_upload',
        },
        auth=(api_token, 'x-auth-token'),
        json={
            'title': title,
            'metadataSchema': metadata_schema,
        }
    )
    r.raise_for_status()
    return r.json()
