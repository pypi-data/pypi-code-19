from .slack import slack_success, slack_error


def send_notification_success(url, title, message, subtitle=None):
    if subtitle is None:
        subtitle = ""
    slack_success(url, title, message, subtitle)


def send_notification_error(url, title, message, subtitle=None):
    if subtitle is None:
        subtitle = ""
    slack_error(url, title, message, subtitle)