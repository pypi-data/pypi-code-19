import aiohttp
import json


async def get_json_response(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            content = await resp.text()

    return json.loads(content)