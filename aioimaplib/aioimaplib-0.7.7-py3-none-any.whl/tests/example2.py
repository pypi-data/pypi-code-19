# -*- coding: utf-8 -*-
import asyncio

import logging

from aioimaplib import aioimaplib

aioimaplib.log.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(module)s:%(lineno)d] %(message)s"))
aioimaplib.log.addHandler(sh)

@asyncio.coroutine
def wait_for_new_message(host, user, password):
    imap_client = aioimaplib.IMAP4_SSL(host=host)
    yield from imap_client.wait_hello_from_server()

    yield from imap_client.login(user, password)
    yield from imap_client.select()

    asyncio.async(imap_client.idle())
    while True:
        msg = yield from imap_client.wait_server_push()
        print('--> received from server: %s' % msg)
        if 'EXISTS' in msg:
            imap_client.idle_done()
            break

    yield from imap_client.logout()


@asyncio.coroutine
def fetch_mail(host, user, password):
    imap_client = aioimaplib.IMAP4_SSL(host=host, timeout=60)
    yield from imap_client.wait_hello_from_server()

    yield from imap_client.login(user, password)
    yield from imap_client.select()

    try:
        while True:
            idle = asyncio.async(imap_client.idle())
            print((yield from imap_client.wait_server_push(60)))
            imap_client.idle_done()
            asyncio.wait_for(idle, 5)

            print((yield from imap_client.uid('fetch', '1:*', '(UID RFC822.SIZE BODY.PEEK[])')))
            print((yield from imap_client.uid('fetch', '1:*', 'FLAGS')))
    finally:
        yield from imap_client.logout()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(fetch_mail('imap-mail.outlook.com', 'tobias.nuxung@outlook.fr', 'TBy2kiagy'))
    # loop.run_until_complete(fetch_mail('imap.mail.yahoo.com', 'paulmercier75@yahoo.com', 'demonstration'))
    loop.run_until_complete(fetch_mail('imap.dune.io', 'projets', 'DUavocatsRR'))
    # loop.run_until_complete(fetch_mail('imap.gmail.com', 'thomasbam@gmail.com', 'GGy2kiagy'))
