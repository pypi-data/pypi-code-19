
import requests
import json


def slack_success(url, title, message, subtitle=None):
    if subtitle is None:
        subtitle = ""
    data = {"attachments": [{"title": title, "pretext": subtitle, "text": message, "color": "#7CD197", "mrkdwn_in": ["text", "pretext"]}]}
    r = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
    if r.status_code == 200:
        return True
    else:
        return False


def slack_error(url, title, message, subtitle=None):
    if subtitle is None:
        subtitle = ""
    text = "```\n%s\n```" % (message)
    data = {"attachments": [{"title": title, "pretext": subtitle, "text": text, "color": "#F02742", "mrkdwn_in": ["text", "pretext"]}]}
    r = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
    if r.status_code == 200:
        return True
    else:
        return False
