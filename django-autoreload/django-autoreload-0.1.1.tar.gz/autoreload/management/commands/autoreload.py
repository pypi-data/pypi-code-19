from __future__ import print_function
import threading
from websocket_server import WebsocketServer
import pyinotify
from django.core.management.base import BaseCommand
from django.conf import settings
from autoreload.conf import WL, EXCLUDE

wm = pyinotify.WatchManager()
mask = pyinotify.IN_MODIFY | pyinotify.IN_CREATE


class EventHandler(pyinotify.ProcessEvent):

    def __init__(self, server):
        self.server = server

    def process_IN_CREATE(self, event):
        print("Creating", event.pathname)

    def process_IN_MODIFY(self, event):
        print("Change in", event.pathname)
        self.server.send_message_to_all("reload")


def new_client(client, server):
    pass


def run(server):
    server.run_forever()


class Command(BaseCommand):
    help = 'Start autoreload daemon'

    def handle(self, *args, **options):
        if settings.DEBUG is False:
            print("This command can only run with DEBUG = True in settings")
            return
        print("Watching file changes in:")
        #excl = pyinotify.ExcludeFilter(EXCLUDE)
        for d in WL:
            print(d)
            path = settings.BASE_DIR + "/" + d
            #wm.add_watch(path, mask, rec=True, exclude_filter=excl)
            wm.add_watch(path, mask, rec=True)

        # run websockets server
        PORT = 9001
        server = WebsocketServer(PORT)
        server.set_fn_new_client(new_client)
        t = threading.Thread(target=run, args=(server,))
        t.start()
        # run watcher
        notifier = pyinotify.ThreadedNotifier(wm, EventHandler(server))
        notifier.loop()
