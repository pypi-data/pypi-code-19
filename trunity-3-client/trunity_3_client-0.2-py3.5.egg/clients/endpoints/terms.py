from trunity_3_client.utils.url import Url, API_ROOT


base_url = Url(API_ROOT)
base_url.tail = 'terms'


class TermsListClient(object):
    _url = base_url.list

    def __init__(self, session):
        self._session = session

    def post(self, site_id, term_title, term_text):
        data = {
            'site_id': site_id,
            'term[title]': term_title,
            'term[text]': term_text,
        }
        response = self._session.post(self._url, data)
        response.raise_for_status()
        return response.json()['term_id']


class TermsClient(object):

    def __init__(self, session):
        self.list = TermsListClient(session)
