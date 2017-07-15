import asyncio
from asyncio import AbstractEventLoop
from typing import Callable

from sc2reader.resources import Replay

from .gameclient import GameClient
from .gamefinishedchecker import check_has_game_finished
from .replayhandler import ReplayHandler
from .uistate import UiState


class ReplayNotifier:
    def __init__(
            self,
            game_client: GameClient,
            most_recent_replay_loader: Callable[[], Replay],
            replay_handler: ReplayHandler,
            event_loop: AbstractEventLoop):

        self.game_client = game_client
        self.load_most_recent_replay = most_recent_replay_loader
        self.replay_handler = replay_handler
        self.event_loop = event_loop

    def handle_replays(self):
        """
        CAUTION! Blocks forever!

        Poll for and handle replays using the provided event loop.
        """

        self.event_loop.run_until_complete(self._poll_for_game_complete())

    async def _poll_for_game_complete(self):
        previous_game_state = await self.game_client.get_current_game_state()

        while True:
            asyncio.sleep(5)

            current_game_state = await self.game_client.get_current_game_state()

            if check_has_game_finished(previous_game_state, current_game_state):
                while True:
                    current_ui_state = await self.game_client.get_current_ui_state()

                    if current_ui_state == UiState.OTHER:
                        break

                    asyncio.sleep(3)

                self.event_loop.create_task(self._find_and_notify_about_most_recent_replay())

            previous_game_state = current_game_state

    async def _find_and_notify_about_most_recent_replay(self):
        # Wait 5 seconds to allow for some time for the replay file to be created.
        asyncio.sleep(5)

        try:
            replay = self.load_most_recent_replay()
        except Exception:
            # No replay found?
            return

        await self.replay_handler.handle_replay(replay)
