import datetime
import logging
import random
import re
import time
from hashlib import sha1
from html import unescape
from json import loads
from urllib.parse import quote, urlencode

from aiohttp import ClientSession

from imdbpie_async.constants import (BASE_URI, DEFAULT_PROXY_URI,
                                     USER_AGENTS)
from imdbpie_async.objects import Episode, Image, Person, Review, Title

logger = logging.getLogger(__name__)


def is_redirection_result(response):
    """
    Return True if response is that of a redirection else False
    Redirection results have no information of use.
    """
    imdb_id = response['data'].get('tconst')
    return (imdb_id and
            imdb_id != response['data'].get('news', {}).get('channel'))


def get_images(response):
    images = []

    for image_data in response.get('data').get('photos', []):
        images.append(Image(image_data))

    return images


class Imdb:
    __slots__ = ('session', 'api_key', 'timestamp', 'user_agent',
                 'locale', 'exclude_episodes', 'proxy_uri', 'anonymize')

    def __init__(self, session: ClientSession, api_key, locale=None,
                 anonymize=False, exclude_episodes=False, proxy_uri=None):
        self.session = session
        self.api_key = sha1(api_key.encode('utf8')).hexdigest()
        self.timestamp = time.mktime(datetime.date.today().timetuple())
        self.user_agent = random.choice(USER_AGENTS)
        self.locale = locale or 'en_US'
        self.exclude_episodes = exclude_episodes
        self.proxy_uri = proxy_uri or DEFAULT_PROXY_URI
        self.anonymize = anonymize

    async def get_person_by_id(self, imdb_id):
        url = self._build_url('/name/maindetails', {'nconst': imdb_id})
        response = await self._get(url)

        if not response or is_redirection_result(response):
            return
        person = Person(response.get('data'))
        return person

    async def get_title_by_id(self, imdb_id):
        url = self._build_url('/title/maindetails', {'tconst': imdb_id})
        response = await self._get(url)

        if not response or is_redirection_result(response):
            return
        if 'data' not in response:
            response['data'] = {}
        # get the full cast information, add key if not present
        response['data']['credits'] = await self._get_credits_data(imdb_id)
        response['data']['plots'] = await self.get_title_plots(imdb_id)

        if self.exclude_episodes \
                and response['data'].get('type') == 'tv_episode':
            return
        title = Title(data=response['data'])
        return title

    async def get_title_plots(self, imdb_id):
        url = self._build_url('/title/plot', {'tconst': imdb_id})
        response = await self._get(url)

        if not response:
            return []
        data = response.get('data', {})
        if data.get('tconst') != imdb_id:
            return []

        plots = data.get('plots', [])
        return [plot.get('text') for plot in plots]

    async def title_exists(self, imdb_id):
        page_url = 'http://www.imdb.com/title/{0}/'.format(imdb_id)

        if self.anonymize is True:
            page_url = self.proxy_uri.format(quote(page_url))

        response = await self.session.head(page_url)

        return 200 <= response.status < 400

    async def search_for_person(self, name):
        search_params = {
            'json': '1',
            'nr': 1,
            'nn': 'on',
            'q': name
        }
        query_params = urlencode(search_params)
        search_results = await self._get(
            'http://www.imdb.com/xml/find?{0}'.format(query_params))
        if not search_results:
            return
        target_result_keys = (
            'name_popular', 'name_exact', 'name_approx', 'name_substring'
        )
        person_results = []

        # Loop through all search_results and build a list
        # with popular matches first
        for key in target_result_keys:
            if key not in search_results:
                continue
            for result in search_results[key]:
                result_item = {
                    'name': unescape(result['name']),
                    'imdb_id': result['id']
                }
                person_results.append(result_item)
        return person_results

    async def search_for_title(self, title):
        default_search_for_title_params = {
            'json': '1',
            'nr': 1,
            'tt': 'on',
            'q': title
        }
        query_params = urlencode(default_search_for_title_params)
        search_results = await self._get(
            'http://www.imdb.com/xml/find?{0}'.format(query_params)
        )
        if not search_results:
            return
        target_result_keys = (
            'title_popular', 'title_exact', 'title_approx', 'title_substring'
        )
        title_results = []

        # Loop through all search_results and build a list
        # with popular matches first
        for key in target_result_keys:
            if key not in search_results:
                continue
            for result in search_results[key]:
                year_match = re.search(r'(\d{4})', result['title_description'])
                year = year_match.group(0) if year_match else None

                result_item = {
                    'title': unescape(result['title']),
                    'year': year,
                    'imdb_id': result['id']
                }
                title_results.append(result_item)

        return title_results

    async def top_250(self):
        url = self._build_url('/chart/top', {})
        response = await self._get(url)
        return response.get('data', {}).get('list', {}).get('list')

    async def popular_shows(self):
        url = self._build_url('/chart/tv', {})
        response = await  self._get(url)
        if not response:
            return
        return response.get('data', {}).get('list')

    async def get_title_images(self, imdb_id):
        url = self._build_url('/title/photos', {'tconst': imdb_id})
        response = await self._get(url)
        if not response:
            return
        return get_images(response)

    async def get_title_reviews(self, imdb_id, max_results=None):
        """Retrieve reviews for a title ordered by 'Best' descending"""
        user_comments = await self._get_reviews_data(
            imdb_id, max_results=max_results
        )

        if not user_comments:
            return

        title_reviews = []

        for review_data in user_comments:
            title_reviews.append(Review(review_data))
        return title_reviews

    async def get_person_images(self, imdb_id):
        url = self._build_url('/name/photos', {'nconst': imdb_id})
        response = await self._get(url)
        if not response:
            return
        return get_images(response)

    async def get_episodes(self, imdb_id):
        if self.exclude_episodes:
            raise ValueError('exclude_episodes is currently set')
        title = await self.get_title_by_id(imdb_id)
        if not title:
            return
        if title.type != 'tv_series':
            raise RuntimeError('Title provided is not of type TV Series')
        url = self._build_url('/title/episodes', {'tconst': imdb_id})
        response = await self._get(url)
        if not response:
            return
        seasons = response.get('data').get('seasons')
        episodes = []
        for season in seasons:
            season_number = season.get('token')
            for idx, episode_data in enumerate(season.get('list')):
                episode_data['series_name'] = title.title
                episode_data['episode'] = idx + 1
                episode_data['season'] = season_number
                e = Episode(episode_data)
                episodes.append(e)

        return episodes

    async def _get_credits_data(self, imdb_id):
        url = self._build_url('/title/fullcredits', {'tconst': imdb_id})
        response = await self._get(url)

        if not response:
            return

        return response.get('data').get('credits')

    async def _get_reviews_data(self, imdb_id, max_results=None):
        params = {'tconst': imdb_id}
        if max_results:
            params['limit'] = max_results
        url = self._build_url('/title/usercomments', params)
        response = await self._get(url)
        if not response:
            return
        return response.get('data').get('user_comments')

    async def _get(self, url):
        resp = await self.session.get(
            url, headers={'User-Agent': self.user_agent}
        )
        async with resp:
            resp.raise_for_status()
            text = await resp.read()
            resp_dict = loads(text.decode('utf-8'))
            if resp_dict.get('error'):
                return None
            return resp_dict

    def _build_url(self, path, params):
        default_params = {
            'api': 'v1',
            'appid': 'iphone1_1',
            'apiPolicy': 'app1_1',
            'apiKey': self.api_key,
            'locale': self.locale,
            'timestamp': self.timestamp
        }
        query_params = dict(**default_params, **params)
        query_params = urlencode(query_params)
        url = f'{BASE_URI}{path}?{query_params}'
        if self.anonymize:
            return self.proxy_uri.format(quote(url))
        return url
