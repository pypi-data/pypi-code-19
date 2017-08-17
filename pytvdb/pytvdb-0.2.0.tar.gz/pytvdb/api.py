from datetime import timedelta

import requests
from ttldict import TTLOrderedDict

from . import models


class TVDB:
    """
    The global entry point for the TVDB api. This object exposes three public fields for accessing te API namespaces:

        - Search
        - Series
        - Episodes
    """

    API_KEY_DEFAULT = 'FF7EF57268A992D6'
    TOKEN_CACHE = TTLOrderedDict(default_ttl=int(timedelta(hours=24).total_seconds()))
    BASE_URL = 'https://api.thetvdb.com'

    def __init__(self, api_key=None, language='en', version=None):
        """
        Create an instance of the TVDB object

        :param api_key: A TVDB api key. This key will be used to make requests. A default key will be used if none is
         provided, but using an application-specific key is recommended
        :param language: The language code to be used when making requests. Default to 'en'
        :param version: The version of the TVDB API to query. Defaults to the latest version
        """
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
        """
        Entry point for the TVDB Search API namespace
        """
        return Search(self)

    def series(self, id):
        """
        Entry point for the TVDB Series API namespace.

        This method is equivalent to the /series/{id} endpoint of the TVDB API
        :param id: The TVDB id of the series to query
        """
        return Series(self, id)

    def episodes(self, id):
        """
        Entry point for the TVDB Episodes API namespace.

        This method is equivalent to the /episodes/{id} endpoint of the TVDB API
        :param id: The TVDB id of the episode to query
        """
        return Episodes(self, id)


class Search:

    def __init__(self, tvdb):
        self._tvdb = tvdb

    def series(self, name='', imdb_id='', zap2it_id=''):
        """
        Searches the TVDB API for a series matching the given parameters.

        Note that only a single parameter may be supplied for a given invocation.
        :param name: A string representing a name to search for
        :param imdb_id: A string representing an IMDB id to search for
        :param zap2it_id: A string representing a zap2it id to search for
        :return: An list of results that match the provided query
        """
        params = {}

        if name:
            params['name'] = name
        if imdb_id:
            params['imdbId'] = imdb_id
        if zap2it_id:
            params['zap2itId'] = zap2it_id

        res = self._tvdb._make_request('/search/series', params)
        return self._tvdb._build_list_of_models(models.SeriesSearchData, res['data'])


class Series(models.SeriesData):

    class EpisodesResult(models.SeriesEpisodes):

        def __init__(self, id, episodes, tvdb):
            super(Series.EpisodesResult, self).__init__(episodes)
            self._tvdb = tvdb
            self._id = id

        def summary(self):
            """
            Returns a summary of the episodes and seasons available for the series

            :return: A summary of the episodes and seasons available for the given series.
            """
            res = self._tvdb._make_request('/series/' + str(self._id) + '/episodes/summary', {})
            return models.SeriesEpisodesSummary(**res['data'])

    def __init__(self, tvdb, id):
        super(Series, self).__init__(**tvdb._make_request('/series/' + str(id), {})['data'])
        self._tvdb = tvdb

    def actors(self):
        """
        Returns actors for the series

        :return: A list of actor objects
        """
        res = self._tvdb._make_request('/series/' + str(self.id) + '/actors', {})
        return self._tvdb._build_list_of_models(models.SeriesActorsData, res['data'])

    def episodes(self):
        """
        All episodes for the series

        :return: A list of episode objects
        """
        res = []
        page = 1

        while True:
            resp = self._tvdb._make_request('/series/' + str(self.id) + '/episodes', {'page': page})
            res += self._tvdb._build_list_of_models(models.BasicEpisode, resp['data'])
            if not resp['links']['next']:
                break
            page = resp['links']['next']
        return self.__class__.EpisodesResult(self.id, res, self._tvdb)


class Episodes(models.Episode):
    def __init__(self, tvdb, id):
        super(Episodes, self).__init__(**tvdb._make_request('/episodes/' + str(id), {})['data'])
        self._tvdb = tvdb
        self._id = id