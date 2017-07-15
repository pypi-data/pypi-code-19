from sc2reader.resources import Replay


class ReplayHandler:

    async def handle_replay(self, replay: Replay):
        raise NotImplementedError()


class NoOpReplayHandler(ReplayHandler):

    async def handle_replay(self, replay: Replay):
        pass