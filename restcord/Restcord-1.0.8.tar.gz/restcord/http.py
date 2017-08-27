import aiohttp
from .vars import __version__ as version
from .vars import __github__ as github

BASE_URL = "https://discordapp.com/api/v6"

class HTTPClient:
	def __init__(self, restcord):
		self.session = aiohttp.ClientSession()
		self.client = restcord

	def get_headers(self):
		headers = {}
		token = self.client.token
		if not self.client.selfbot:
			token = "Bot {}".format(token)
		headers['Authorization'] = token
		headers['User-Agent'] = "RestCord Python ({}, v{})".format(github, version)
		return headers

	async def get(self, endpoint):
		resp = await self.session.get(BASE_URL + endpoint, headers=self.get_headers())
		return await resp.json()

	async def post(self, endpoint, data=None):
		resp = await self.session.post(BASE_URL + endpoint, headers=self.get_headers(), json=data)
		return await resp.json()

	async def delete(self, endpoint):
		resp = await self.session.delete(BASE_URL + endpoint, headers=self.get_headers())
		return await resp.json()

	async def head(self, endpoint):
		resp = await self.session.head(BASE_URL + endpoint, headers=self.get_headers())
		return await resp.json()

	async def options(self, endpoint):
		resp = await self.session.options(BASE_URL + endpoint, headers=self.get_headers())
		return await resp.json()

	async def patch(self, endpoint, data=None):
		resp = await self.session.patch(BASE_URL + endpoint, headers=self.get_headers(), json=data)
		return await resp.json()