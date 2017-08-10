from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants


class WP1(WaitPage):
    group_by_arrival_time = True

    def get_players_for_group(self, waiting_players):
        if len(waiting_players) >= 2:
            return waiting_players

class WP2(WaitPage): pass

class MyPage(Page):
    pass




class Results(Page):
    pass


page_sequence = [
    WP1, WP2, #WP3, WP4, WP5, WP6, WP7,
    MyPage,
]
