from sc2replaynotifier import ReplayHandler

from .replayanalysisserviceclient import ReplayAnalysisServiceClient as _ReplayAnalysisServiceClient
from .trainingassistantclient import TrainingAssistantClient as _TrainingAssistantClient
from .trainingassistantreplayhandler import TrainingAssistantReplayHandler as _TrainingAssistantReplayHandler


def create_training_assistant_replay_handler(
        replay_analysis_service_host: str,
        training_assistant_host: str) -> ReplayHandler:

    replay_analysis_service_client = _ReplayAnalysisServiceClient(replay_analysis_service_host)
    training_assistant_client = _TrainingAssistantClient(training_assistant_host)
    return _TrainingAssistantReplayHandler(
        replay_analysis_service_client.analyse_replay,
        training_assistant_client.upload_replay_analysis,
        training_assistant_client.open_replay_analysis_in_browser,
        lambda x: print(x))
