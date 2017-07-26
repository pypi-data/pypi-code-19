import aiohttp

ADD_REPLAY_ANALYSIS_ENDPOINT = "/submit"


class ReplayAnalysisServiceClient:

    def __init__(self, replay_analysis_service_host: str):
        self.add_replay_analysis_endpoint = replay_analysis_service_host + ADD_REPLAY_ANALYSIS_ENDPOINT

    async def analyse_replay(self, replay_path) -> dict:
        replay_file = open(replay_path, "rb")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.add_replay_analysis_endpoint, data=replay_file) as resp:
                    if str(resp.status).startswith("2"):
                        return await resp.json()
        finally:
            replay_file.close()

        return {}
