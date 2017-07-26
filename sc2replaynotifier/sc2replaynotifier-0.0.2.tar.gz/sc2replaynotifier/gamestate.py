from typing import List, Tuple
from enum import Enum


class GameStateType(Enum):
    NOT_STARTED = 1
    IN_PROGRESS = 2
    FINISHED = 3


class GameState:

    def __init__(self, state_type: GameStateType, game_time: int, players: List[Tuple[str, str]]):
        self.state_type = state_type
        self.game_time = game_time
        self.players = players


def not_started() -> GameState:
    return GameState(GameStateType.NOT_STARTED, 0, [])


def in_progress(game_time: int, players: List[Tuple[str, str]]) -> GameState:
    return GameState(GameStateType.IN_PROGRESS, game_time, players)


def finished(game_time: int, players: List[Tuple[str, str]]) -> GameState:
    return GameState(GameStateType.FINISHED, game_time, players)
