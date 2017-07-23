# coding: utf8
import logging

from kalliope import SettingLoader, SynapseLauncher
from kalliope.core.ConfigurationManager import BrainLoader
from kalliope.core.Players import Mplayer
from kalliope.core.Players.PlaySoundPlayer import PlaySoundPlayer
from kalliope.core.Players.PyAlsaAudioPlayer import PyAlsaAudioPlayer

logging.basicConfig()
logger = logging.getLogger("kalliope")
logger.setLevel(logging.DEBUG)

brain = BrainLoader().get_brain()
settings = SettingLoader().settings

import time


order = "quelle heure est-il"
SynapseLauncher.run_matching_synapse_from_order(order_to_process=order, brain=brain, settings=settings)



