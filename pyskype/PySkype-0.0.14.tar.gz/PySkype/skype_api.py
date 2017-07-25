import os
import requests
from .utils import _logger


def get_attachment(token, service_url, name, message_id, attachments_dir):
    """Extracting attachment from conversation
    :param token: <str> - Microsoft Bots API access token
    :param service_url: <str> - attachment URL
    :param name: <str> - filename
    :param message_id: <str> - id of message, for adding to filename
    :param attachments_dir: <str> - path, where to save attachments from Skype
    :return: <str> - path to downloaded file or None
    """
    try:
        _logger.info('Extracting attachment')
        # getting data from Bots API
        authorization = "Bearer {}".format(token)
        request = requests.get(
            service_url,
            headers={"Authorization": authorization, "Content-Type": "application/json"}
        )
        if request.status_code == 200:
            _logger.info('Data were received. Status code 200')
            # creating directory for loaded attachment, if it doesn't exists
            attachment_dir = '{}/attachments'.format(attachments_dir)
            if not os.path.exists(attachment_dir):
                os.makedirs(attachment_dir)
            attachment = '{}/{}_{}'.format(attachment_dir, message_id, name)
            with open(attachment, 'wb') as attached_file:
                attached_file.write(request.content)
            _logger.info('Attachment successfully saved')
            return os.path.abspath(attachment)
        else:
            _logger.warning("Data weren't received. Status code: {}".format(request.status_code))
    except Exception as e:
        _logger.error(e)
        return None


def send_message(token, service_url, sender_id, text):
    """Sending message from Bot
    :param token: <str> - Microsoft Bots API access token
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
        authorisation = "Bearer {}".format(token)
        request = requests.post(
            url,
            headers={"Authorization": authorisation, "Content-Type": "application/json"},
            json=payload
        )
        if request.status_code == 200:
            _logger.info('Data were sent. Status code 200')
        else:
            _logger.info('Data were sent. Status code: {}'.format(request.status_code))
    except Exception as e:
        _logger.error(e)


def send_media_message(token, service_url, sender_id, media_type, url):
    """Sending media message from Bot
    :param token: <str> - Microsoft Bots API access token
    :param service_url: <str> - attachment URL 
    :param sender_id: <str> - sender Skype id 
    :param media_type: <str> - content type of media data
    :param url: <str> - URL of media data 
    """
    try:
        payload = {
            "type": "message",
            "attachments": [{
                "contentType": media_type,
                "contentUrl": url
            }]
        }
        url = '{}/v3/conversations/{}/activities/'.format(service_url, sender_id)
        authorisation = "Bearer {}".format(token)
        request = requests.post(
            url,
            headers={"Authorization": authorisation, "Content-Type": "application/json"},
            json=payload
        )
        _logger.info('Status code: {}'.format(request.status_code))
    except Exception as e:
        _logger.error(e)
