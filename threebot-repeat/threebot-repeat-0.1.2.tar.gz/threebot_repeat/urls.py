"""URLs for the threebot_repeat app."""
from django.conf.urls import url

from threebot_repeat import views


urlpatterns = [
    url(r'^$',
        views.list,
        name='threebot_repeat_list'),
    url(r'^repeat-and-replay-log/(?P<log_id>[-\d]+)/$',
        views.replay_and_repeat,
        name='threebot_replay_and_repeat', ),
    url(r'^stop-repetition/(?P<bg_task_id>[-\d]+)/$',
        views.stop_repetition,
        name='threebot_replay_stop_repetition', ),
]
