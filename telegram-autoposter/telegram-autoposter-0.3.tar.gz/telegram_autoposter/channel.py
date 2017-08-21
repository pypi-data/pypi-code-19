from telegram.ext import Updater


class Channel(object):
    name = '@channel'
    pipe_classes = []

    def __init__(self, updater: Updater):
        """
        - name: name of channel in telegram. **Must** starts with "@".
        - label: identifier for channel. **Must** be unique.
        - pipe_classes:
        - commands_handlers: list of command handlers which would be attached when we need them and detached when we don't.

        :param updater: bot updater.
        """
        self.label = self.__class__.__name__
        self.updater = updater
        self.dispatcher = updater.dispatcher
        self.commands_handlers = []

    def start_posting(self):
        """
        Schedule posting for each pipe.
        """
        for pipe_class in self.pipe_classes:
            pipe = pipe_class(self.name, self.updater)
            pipe.schedule_posts()

    def add_commands_handlers(self):
        """
        Used by manager class when changing channel command namespace.
        """
        for handler in self.commands_handlers:
            self.dispatcher.add_handler(handler)

    def remove_commands_handlers(self):
        """
        Used by manager class when changing channel command namespace.
        """
        for handler in self.commands_handlers:
            self.dispatcher.remove_handler(handler)

    def help_text(self):
        """
        Used by manager class to print out info about commands specified for channel.
        """
        pass
