from telegram.ext import Updater


class Channel(object):
    name = 'channel'
    pipe_classes = []
    commands_handlers = []

    def __init__(self, updater: Updater):
        self.updater = updater
        self.dispatcher = updater.dispatcher
        self.store = None

    def start_posting(self):
        for pipe_class in self.pipe_classes:
            pipe = pipe_class(self.name, self.updater)
            pipe.schedule_posts()

    def add_commands_handlers(self):
        for handler in self.commands_handlers:
            self.dispatcher.add_handler(handler)

    def remove_commands_handlers(self):
        for handler in self.commands_handlers:
            self.dispatcher.remove_handler(handler)

    def help_text(self):
        pass

