import logging

from telegram.ext import Updater

from .fetcher import Fetcher
from .filters import Filter
from .modeller import Modeller
from .poster import Poster
from .scheduler import Scheduler


class Pipe(object):
    post_interval = 60
    fetcher_class = Fetcher
    modeller_class = Modeller
    filter_classes = ()
    poster_class = Poster

    def __init__(self, channel_id: str, updater: Updater):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.channel_id = channel_id
        self.updater = updater
        self.scheduler = Scheduler(self.updater.job_queue)

    def schedule_posts(self):
        self.scheduler.stop()
        self.pre_schedule_hook()
        self.scheduler.add_job(self.post, self.post_interval)

    def pre_schedule_hook(self):
        pass

    def pre_post_hook(self):
        pass

    def post(self):
        self.pre_post_hook()
        data = self.fetch_data()
        data = self.pre_model_filtration(data)
        data = self.model_data(data)
        data = self.post_model_filtration(data)
        self.post_data(data)

    def fetch_data(self):
        fetcher = self.fetcher_class()
        return fetcher.fetch()

    def pre_model_filtration(self, data):
        return data

    def model_data(self, data):
        modeller = self.modeller_class()
        return modeller.model(data)

    def post_model_filtration(self, data):
        for filter_class in self.filter_classes:
            filter: Filter = filter_class()
            data = filter.filter(data)
        return data

    def post_data(self, data):
        poster = self.poster_class(self.channel_id, self.updater)
        poster.post(data)
