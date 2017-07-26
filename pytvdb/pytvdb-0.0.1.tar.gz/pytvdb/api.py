from datetime import timedelta

import requests
from ttldict import TTLOrderedDict

from . import models


class TVDB:

    API_KEY_DEFAULT = 'FF7EF57268A992D6'
    TOKEN_CACHE = TTLOrderedDict(default_ttl=int(timedelta(hours=24).total_seconds()))
    BASE_URL = 'https://api.thetvdb.com'

    def __init__(self, api_key=None, language='en', version=None):
        self._api_key = api_key or TVDB.API_KEY_DEFAULT
        self._language = language
        if version:
            self._version = version

    def _make_request(self, route, params):
        token = self._get_token()
        headers = self._build_headers(token)
        r = requests.get(self.__class__.BASE_URL + route, params=params, headers=headers)
        r.raise_for_status()
        return r.json()

    def _build_headers(self, api_token):
        headers = {
            'Authorization': 'Bearer ' + api_token,
            'Accept-Language': self._language,
            'Accept': 'application/json'
        }

        try:
            headers['Accept'] = 'application/vnd.thetvdb.v' + self._version
        except AttributeError: pass

        return headers

    def _get_token(self):
        try:
            return self.__class__.TOKEN_CACHE['token']
        except KeyError:
            headers = {'Content-Type': 'application/json'}
            payload = {'apikey': self._api_key}
            r = requests.post(self.__class__.BASE_URL + '/login', json=payload, headers=headers)
            r.raise_for_status()
            token = r.json()['token']
            self.__class__.TOKEN_CACHE['token'] = token
            return token

    def _build_list_of_models(self, func, iterable):
        return [func(**d) for d in iterable]

    def search(self):
        return Search(self)

    def series(self, id):
        return Series(self, id)


class Search:

    def __init__(self, tvdb):
        self._tvdb = tvdb

    def series(self, name='', imdb_id='', zap_2_it_id=''):
        params = {}

        if name:
            params['name'] = name
        if imdb_id:
            params['imdbId'] = imdb_id
        if zap_2_it_id:
            params['zap2itId'] = zap_2_it_id

        res = self._tvdb._make_request('/search/series', params)
        return self._tvdb._build_list_of_models(models.SeriesSearchData, res['data'])


class Series(models.SeriesData):

    class EpisodesResult(models.SeriesEpisodes):

        def __init__(self, episodes, tvdb):
            super(Series.EpisodesResult, self).__init__(episodes)
            self._tvdb = tvdb

        def summary(self):
            res = self._tvdb._make_request('/series/' + str(self.id) + '/episodes/summary', {})
            return models.SeriesEpisodesSummary(**res['data'])

    def __init__(self, tvdb, id):
        super(Series, self).__init__(**tvdb._make_request('/series/' + str(id), {})['data'])
        self._tvdb = tvdb

    def actors(self):
        res = self._tvdb._make_request('/series/' + str(self.id) + '/actors', {})
        return self._tvdb._build_list_of_models(models.SeriesActorsData, res['data'])

    def episodes(self):
        res = []
        page = 1

        while True:
            resp = self._tvdb._make_request('/series/' + str(self.id) + '/episodes', {'page': page})
            res += self._tvdb._build_list_of_models(models.BasicEpisode, resp['data'])
            if not resp['links']['next']:
                break
            page = resp['links']['next']
        return self.__class__.EpisodesResult(res, self._tvdb)