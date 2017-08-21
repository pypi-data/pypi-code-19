"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.utils.crypto import PubCrypto
from pubkeeper.topic import Topic
from Crypto import Random
from Crypto.Cipher import AES
from binascii import hexlify, unhexlify
from uuid import uuid4
from threading import Lock


class Brewer(Topic):
    def __init__(self, *args, brewer_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.brewer_id = brewer_id or uuid4().hex
        self.brewing = {}
        self.brews = []
        self.brew_lock = Lock()

        self._crypto = None
        if self.crypto:
            self._crypto = {
                'mode': AES.MODE_CBC,
                'key': hexlify(Random.new().read(16)).decode()
            }
            self._cipher = PubCrypto(
                self._crypto['mode']
            )

    def get_config(self):
        ret = {}

        if self.crypto:
            ret['cipher'] = self._crypto

        return ret

    def new_patron(self, patron_id, patron_brew):
        with self.topic_lock:
            brew = self.get_brew(patron_brew['name'])

            if brew is None:
                raise RuntimeError("Brewer could not match a parity brew for "
                                   "patron brew: {}".format(patron_brew))

            if patron_id in self.brewing:
                self.remove_patron(patron_id)

            if brew not in self.brewing:
                self.brewing[brew] = {
                    patron_id: patron_brew
                }
            else:
                self.brewing[brew][patron_id] = patron_brew

            brew.start_brewer(self.brewer_id,
                              self.topic,
                              patron_id,
                              patron_brew)

            self.logger.info("Started brewer for {}:{}".format(
                self.topic, patron_id
            ))

    def remove_patron(self, patron_id):
        with self.topic_lock:
            for brew, patrons in self.brewing.copy().items():
                if patron_id in patrons:
                    brew.stop_brewer(self.brewer_id,
                                     self.topic,
                                     patron_id)

                    del(self.brewing[brew][patron_id])

                if len(self.brewing[brew]) == 0:
                    del(self.brewing[brew])

                self.logger.info("Stopped brewer for {}:{}".format(
                    self.topic, patron_id
                ))

    def brew(self, data):
        with self.brew_lock:
            if self.crypto:
                data = self._cipher.encrypt(
                    unhexlify(self._crypto['key']),
                    data
                )

            for brew, patrons in self.brewing.items():
                brew.brew(self.brewer_id,
                          self.topic,
                          data,
                          patrons)
