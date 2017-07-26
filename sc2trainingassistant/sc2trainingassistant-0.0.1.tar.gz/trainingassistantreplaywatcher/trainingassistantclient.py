import webbrowser

import aiohttp

ADD_REPLAY_ANALYSIS_ENDPOINT = "/add/"
SHOW_REPLAY_ANALYSIS_ENDPOINT = "/analysis.html?hash="


class TrainingAssistantClient:

    def __init__(self, url: str):
        self._add_replay_analysis_endpoint = url + ADD_REPLAY_ANALYSIS_ENDPOINT
        self._show_replay_analysis_endpoint = url + SHOW_REPLAY_ANALYSIS_ENDPOINT

    async def upload_replay_analysis(self, replay_analysis: dict) -> dict:
        async with aiohttp.ClientSession() as session:
            url = self._add_replay_analysis_endpoint + replay_analysis["hash"]
            async with session.put(url, json=replay_analysis) as resp:
                return await resp.json()

    def open_replay_analysis_in_browser(self, replay_hash: str) -> None:
        webbrowser.open_new_tab(self._show_replay_analysis_endpoint + replay_hash)
