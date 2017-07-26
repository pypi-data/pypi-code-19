from .gamestate import GameState, not_started, in_progress, finished
from .uistate import UiState


class GameClient:

    def __init__(self, game_object_getter, ui_object_getter):
        self.get_game_object = game_object_getter
        self.get_ui_object = ui_object_getter

    async def get_current_game_state(self) -> GameState:
        try:
            game_object = await self.get_game_object()

            if not game_object.get("players", []) or game_object.get("isReplay", True):
                return not_started()
            else:
                game_time = game_object.get("displayTime", 0)
                player_names = [player.get("name", "") for player in game_object["players"]]
                player_races = [player.get("race", "") for player in game_object["players"]]

                player_info = list(zip(player_names, player_races))

                if any(player.get("result", "Undecided") == "Undecided" for player in game_object["players"]):
                    return in_progress(game_time, player_info)
                else:
                    return finished(game_time, player_info)

        except Exception:
            return not_started()

    async def get_current_ui_state(self) -> GameState:
        try:
            ui_object = await self.get_ui_object()

            if not ui_object.get("activeScreens", []):
                return UiState.IN_GAME
            else:
                return UiState.OTHER

        except Exception:
            return UiState.OTHER