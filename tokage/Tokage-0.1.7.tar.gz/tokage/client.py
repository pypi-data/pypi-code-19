import aiohttp
from .abc import *
from .errors import *

BASE_URL = 'https://jikan.me/api/v1.1/'
ANIME_URL = BASE_URL + 'anime/'
MANGA_URL = BASE_URL + 'manga/'
PERSON_URL = BASE_URL + 'person/'
CHARACTER_URL = BASE_URL + 'character/'

class Client:
    def __init__(self, session=aiohttp.ClientSession()):
        self.session = session

    async def request(self, url):
        async with self.session.get(url) as resp:
            return await resp.json()

    async def get_anime(self, target_id):
        response_json = await self.request(ANIME_URL + str(target_id))
        if response_json is None:
            raise AnimeNotFound("Anime with the given ID was not found")
        result = Anime(target_id, **response_json)
        return result

    async def get_manga(self, target_id):
        response_json = await self.request(MANGA_URL + str(target_id))
        if response_json is None:
            raise MangaNotFound("Manga with the given ID was not found")
        result = Manga(target_id, **response_json)
        return result

    async def get_character(self, target_id):
        response_json = await self.request(CHARACTER_URL + str(target_id))
        if response_json is None:
            raise CharacterNotFound("Character with the given ID was not found")
        result = Character(target_id, **response_json)
        return result

    async def get_person(self, target_id):
        response_json = await self.request(PERSON_URL + str(target_id))
        if response_json is None:
            raise PersonNotFound("Person with the given ID was not found")
        result = Person(target_id, **response_json)
        return result
