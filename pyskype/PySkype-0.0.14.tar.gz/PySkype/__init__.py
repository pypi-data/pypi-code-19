import threading
import requests
import time
from . import skype_api


class SkypeBot:
    def __init__(self, client_id, client_secret, attachments_dir):
        self.attachments_dir = attachments_dir

        def token_func():
            global token
            payload = 'grant_type=client_credentials&client_id={}' \
                      '&client_secret={}' \
                      '&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default'.format(client_id, client_secret)
            login_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token?client_id={}" \
                        "&client_secret={}" \
                        "&grant_type=client_credentials&scope=" \
                        "https%3A%2F%2Fgraph.microsoft.com%2F.default".format(client_id, client_secret)
            request = requests.post(
                login_url,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            data = request.json()
            token = data["access_token"]

        def thread_target():
            while True:
                token_func()
                time.sleep(3000)

        self.t = threading.Thread(target=thread_target)
        self.t.daemon = True
        self.t.start()

    def send_message(self, service, sender, text):
        return skype_api.send_message(token, service, sender, text)

    def get_attachment(self, service, name, message_id):
        return skype_api.get_attachment(token, service, name, message_id, self.attachments_dir)

    def send_media(self, service, sender, media_type, url):
        return skype_api.send_media_message(token, service, sender, media_type, url)
