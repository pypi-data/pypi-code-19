from .gamestate import GameState, GameStateType


def check_has_game_finished(previous_game_state: GameState, current_game_state: GameState) -> bool:
    return (
        (previous_game_state.state_type == GameStateType.IN_PROGRESS
            and (current_game_state.state_type == GameStateType.FINISHED
                or previous_game_state.players != current_game_state.players))
        or (current_game_state.state_type == GameStateType.FINISHED
            and (previous_game_state.state_type != GameStateType.FINISHED
                 or previous_game_state.players != current_game_state.players)))
