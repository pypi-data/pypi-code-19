from sc2reader.resources import Replay


def frame_to_second(frame: int, replay: Replay = None) -> float:
    fps = replay.game_fps if replay is not None else 16

    return frame / (1.4 * fps)