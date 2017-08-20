#!/bin/python
import roomai.common
import random
from roomai.fivecardstud import FiveCardStudEnv

class FiveCardStudRandomPlayer(roomai.common.AbstractPlayer):
    """
    """

    public_state = None
    person_state = None
    def receive_info(self, info):
        """

        Args:
            info:
        """
        self.public_state = info.public_state
        self.person_state = info.person_state

    def take_action(self):
        """

        Returns:

        """
        actions = FiveCardStudEnv.available_actions(self.public_state, self.person_state).values()
        idx     = int(random.random() * len(actions))
        return actions[idx]

    def reset(self):
        """

        """
        pass
