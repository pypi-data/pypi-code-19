"""
Simple Slack (legacy) client which polls messages and images from a given channel.
"""
import atexit
from datetime import datetime
from os import remove
from tempfile import NamedTemporaryFile
from threading import Timer, Thread, Lock

from httplib2 import Http
from slackclient import SlackClient

from .configreader import Config


class SlackInfoClient(SlackClient):
    """
    Simple Slack client
    """
    def __init__(self, config_file=None, default_image=None, token=None, channel=None, http=None):
        """
        Create a Slack client.

        :param config_file: path to config file
        :param default_image:  path to default image
        :param token:  Slack legacy authentication token
        :param channel: Slack channel ID
        :param http: Http instance
        """

        # get config from environment
        self.config = Config()

        if config_file:
            self.config.read(config_file)

        if token:
            self.config.token = token

        if channel:
            self.config.channel = channel

        self.default_image = default_image

        self.img = []
        self.msg = []
        self.update_stamp = None
        self.message_stamp = None

        self.msg_limit = 5
        self.img_limit = 1

        self.data_lock = Lock()
        self.auto_time = None
        self.thread = None

        if http:
            self.http = http
        else:
            self.http = Http('.cache')

        atexit.register(self.cleanup)

        super(SlackInfoClient, self).__init__(self.config.token)

    def cleanup(self):
        for f in self.img:
            try:
                remove(f)
                print("Image %s deleted." % f)
            except IOError:
                print("Deletion of image %s failed!" % f)

    def request(self):
        if self.thread and self.thread.is_alive():
            raise IOError("Request is already running!")
        else:
            self.thread = Thread(target=self.request_runner)
            self.thread.start()

    def request_runner(self):
        """
        Request Slack channel data
        """
        history = self.api_call("channels.history", channel=self.config.channel, limit=self.msg_limit + self.img_limit)

        texts = []
        img_msgs = []

        if not history or not 'messages' in history:
            print("Invalid Slack history! %s" % history)
            return

        messages = history['messages']
        # sort messages by time
        messages.sort(key=lambda m: m['ts'])

        if messages:
            with self.data_lock:
                self.message_stamp = messages[0]['ts']

        for message in messages:
            if message['type'] == 'message':
                text = message['text']
                # ignore (some) system messages
                if text[0] != '<':
                    # try to get user name
                    user = ""
                    user_info = self.api_call("users.info", user=message['user'], limit=1)
                    if 'user' in user_info:
                        if 'name' in user_info['user']:
                            user = user_info['user']['name']
                    # append to text messages
                    texts.append("%s: %s" % (user, text))

                # check if message has a file
                if 'file' in message:
                    # if file is a (accepted) image
                    if str(message['file']['mimetype']) == 'image/jpeg':
                        img_msgs.append(message)

        img_files = []

        # download images
        for msg in img_msgs:
            # sort images by time
            img_msgs.sort(key=lambda m: m['ts'])
            url = msg['file']['url_private_download']
            file = self.download(url)
            if file:
                img_files.append(file)

        self.update_data(texts, img_files)

    def download(self, url):
        # open image URL
        response, content = self.http.request(url, headers={'Authorization': 'Bearer %s' % self.token})
        if response.status == 200:
            file = NamedTemporaryFile(prefix="slack_img", suffix=".jpg", delete=False)
            file.write(content)
            file.flush()
            file.close()
            return file.name
        else:
            return None

    def update_data(self, messages, images):
        """
        Update data cache.

        :param messages: messages from channel
        :param images:  images form channel
        """
        old = []

        with self.data_lock:
            msgs = messages + self.msg
            self.msg = msgs[:self.msg_limit]

            imgs = images + self.img
            self.img = imgs[:self.img_limit]
            old += imgs[self.img_limit:]

            self.update_stamp = datetime.now()

        for o in old:
            try:
                remove(o)
            except IOError:
                print("Old image %s was not deleted!" % o)

        if self.auto_time:
            Timer(self.auto_time, self.request)

    def update_time(self):
        """
        Get timestamp of latest update.
        """
        return self.update_stamp

    def is_updating(self):
        """
        Is a data request running at the moment?
        """
        if not self.thread:
            return False
        else:
            return self.thread.is_alive()

    def auto_update(self, seconds=3600):
        """
        Start auto update.

        :param seconds: auto update interval
        """
        self.auto_time = seconds
        self.request()

    def messages(self, limit=None):
        """
        Get cached messages.

        :param limit: message number limit
        :return: messages as list
        """
        if not limit:
            limit = self.msg_limit

        with self.data_lock:
            return self.msg[:limit]

    def images(self, limit=None):
        """
        Get cached images.

        :param limit: image number limit
        :return: images as list
        """
        if not limit:
            limit = self.img_limit

        with self.data_lock:
            return self.img[:limit]
