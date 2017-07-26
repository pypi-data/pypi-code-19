from trainingassistantreplaywatcher import create_training_assistant_replay_handler
from sc2replaynotifier import create_replay_notifier


def main():
    replay_handler = create_training_assistant_replay_handler(
        "http://allinbot.cloudapp.net/replay-analysis",
        "http://allinbot.cloudapp.net/training-assistant")

    replay_notifier = create_replay_notifier(replay_handler)

    print("Waiting for replays...")
    replay_notifier.handle_replays()


if __name__ == "__main__":
    main()