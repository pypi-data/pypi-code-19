import importlib
import logging

from . import config

class Manager(object):
    def __init__(self, sender):
        logging.info('creating manager')
        self.sender = sender
        self.threads = {}

    def start(self):
        self.start_routines(config.DEFAULT_ROUTINES)

    def start_routines(self, routines):
        for routine_name in routines:
            if not routine_name in self.threads:
                logging.info("starting routine " + str(routine_name))
                module = importlib.import_module('unicornclient.routines.' + routine_name)
                routine = module.Routine()
                routine.manager = self
                routine.daemon = True
                routine.start()
                self.threads[routine_name] = routine

    def join(self):
        for thread in self.threads.values():
            thread.join()

    def forward(self, name, task):
        if name == 'routines':
            routines = task['list'] if 'list' in task else []
            self.start_routines(routines)
            return

        if name in self.threads:
            self.threads[name].queue.put(task)
            return

    def send(self, message):
        self.sender.send(message)

    def authenticate(self):
        self.forward('auth', True)
