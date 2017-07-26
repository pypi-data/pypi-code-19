class ReplayHandler:

    async def handle_replay(self, replay_path: str):
        raise NotImplementedError()


class NoOpReplayHandler(ReplayHandler):

    async def handle_replay(self, replay_path: str):
        pass