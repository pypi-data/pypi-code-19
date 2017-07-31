import requests
import json
from functools import wraps
from .skype_api_tools import get_attachment_path
from .utils import _logger


def get_token(client_id, client_secret):
    payload = 'grant_type=client_credentials&client_id={}' \
              '&client_secret={}' \
              '&scope=https%3A%2F%2Fapi.botframework.com%2F.default'.format(client_id, client_secret)
    login_url = "https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token?client_id={}" \
                "&client_secret={}" \
                "&grant_type=client_credentials&scope=" \
                "https%3A%2F%2Fapi.botframework.com%2F.default".format(client_id, client_secret)
    request = requests.post(
        login_url,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    data = request.json()
    try:
        token = data["access_token"]
    except KeyError as invalid_credentials:
        if data['error'] == 'invalid_client':
            raise KeyError('Invalid or empty credentials')
        else:
            raise
    return token


class Message:
    def __init__(self, api_json):
        self.channel = api_json['channelId']
        self.message_time = api_json['timestamp']
        self.message_type = api_json['type']
        self.username = api_json['from']['name']
        self.user_id = api_json['from']['id']
        self.message_id = api_json['id']
        self.client_platform = api_json['entities'][0]['platform']
        self.encoding = api_json['entities'][0]['locale']
        if self.message_type == 'contactRelationUpdate':
            self.action = api_json['action']
        elif self.message_type == 'message':
            self.message_text = api_json['text']
            self.service_url = api_json['serviceUrl']


class SkypeBot:
    """
    Main functionality:
    - creating token from bot credentials to receiving and sending messages
    - sending messages from bot
    - getting attachments

    """

    def __init__(self, client_id, client_secret, attachments_dir):
        self.client_id = client_id
        self.client_secret = client_secret
        self.attachments_dir = attachments_dir
        self.token = get_token(self.client_id, self.client_secret)

    def send_message(self, service_url, sender_id, text):
        """Sending message from Bot
        :param service_url: <str> - attachment URL 
        :param sender_id: <str> - sender Skype id  
        :param text: <str> - text to send
        """
        try:
            payload = {
                "type": "message",
                "text": text
            }
            url = '{}/v3/conversations/{}/activities/'.format(service_url, sender_id)
            authorisation = "Bearer {}".format(self.token)
            request = requests.post(
                url,
                headers={"Authorization": authorisation, "Content-Type": "application/json"},
                json=payload
            )
            if request.status_code == 200:
                _logger.info('Data were sent. Status code 200')
            elif request.status_code == 403:
                authorisation = "Bearer {}".format(self.token)
                request = requests.post(
                    url,
                    headers={"Authorization": authorisation, "Content-Type": "application/json"},
                    json=payload
                )
            else:
                _logger.info('Data were sent. Status code: {}'.format(request.status_code))
        except Exception as e:
            _logger.error(e)

    def get_attachment(self, service_url, name, message_id):
        """Extracting attachment from conversation
            :param service_url: <str> - attachment URL
            :param name: <str> - filename
            :param message_id: <str> - id of message, for adding to filename
            :return: <str> - path to downloaded file or None
            """
        try:
            _logger.info('Extracting attachment')
            # getting data from Bots API
            authorization = "Bearer {}".format(self.token)
            request = requests.get(
                service_url,
                headers={"Authorization": authorization, "Content-Type": "application/json"}
            )
            if request.status_code == 200:
                _logger.info('Data were received. Status code 200')
                return get_attachment_path(request, self.attachments_dir, message_id, name)
            elif request.status_code == 403:
                authorization = "Bearer {}".format(self.token)
                request = requests.get(
                    service_url,
                    headers={"Authorization": authorization, "Content-Type": "application/json"}
                )
                return get_attachment_path(request, self.attachments_dir, message_id, name)
            else:
                _logger.warning("Data weren't received. Status code: {}".format(request.status_code))
        except Exception as e:
            _logger.error(e)
            return None

    def send_media(self, service_url, sender_id, media_type, url):
        try:
            payload = {
                "type": "message",
                "attachments": [{
                    "contentType": media_type,
                    "contentUrl": url
                }]
            }
            url = '{}/v3/conversations/{}/activities/'.format(service_url, sender_id)
            authorisation = "Bearer {}".format(self.token)
            request = requests.post(
                url,
                headers={"Authorization": authorisation, "Content-Type": "application/json"},
                json=payload
            )
            _logger.info('Status code: {}'.format(request.status_code))
        except Exception as e:
            _logger.error(e)

    def message_handler(self, request, **options):
        """ Decorator for extracting all data from received request  
        :param request: <obj> - request with data
        :param options: 
        :return: 
        """

        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                api_json = json.loads(request.data.decode('utf8'))
                message = Message(api_json)
                # here we need a code to wrap the request
                return f(message, **kwargs)

            return decorated_function

        return decorator
