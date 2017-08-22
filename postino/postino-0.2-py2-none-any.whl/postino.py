# coding: utf-8
import functools

from .constants import DEFAULT_STR_ENCODING
from .constants import DEFAULT_STR_ENCODING_ERRORS
from .construct import construct
from .send import send_message


def postino(
        text='',
        html='',
        subject='',
        to=[],
        cc=[],
        bcc=[],
        fromaddr=[],
        date=None,
        host='localhost',
        port=25,
        mode=None,
        login=None,
        password=None,
        encoding=DEFAULT_STR_ENCODING,
        encoding_errors=DEFAULT_STR_ENCODING_ERRORS):

    message, fromline, recipients = construct(
        text=text,
        html=html,
        subject=subject,
        to=to,
        cc=cc,
        bcc=bcc,
        fromaddr=fromaddr,
        date=date,
        encoding=encoding,
        encoding_errors=encoding_errors)

    send_message(
        message,
        recipients,
        fromline,
        host=host,
        port=port,
        mode=mode,
        login=login,
        password=password)


def Sender(**kwargs):
    return functools.partial(postino, **kwargs)
