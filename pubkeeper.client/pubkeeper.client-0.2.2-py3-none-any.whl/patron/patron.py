"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.utils.crypto import PubCrypto
from pubkeeper.topic import Topic
from binascii import unhexlify
from uuid import uuid4


class Patron(Topic):
    def __init__(self, *args, callback=None, patron_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.patron_id = patron_id or uuid4().hex
        self.callback = callback
        self.brews = []
        self.ciphers = {}

        self.patroning = {}

    def new_brewer(self, topic, brewer_id, brewer_config, brewer_brew):
        with self.topic_lock:
            brew = self.get_brew(brewer_brew['name'])

            if brew is None:
                raise RuntimeError("Patron could not match a parity brew for "
                                   "brewer brew: {}".format(brewer_brew))

            if brewer_id in self.patroning:
                self.remove_brewer(brewer_id)

            self.patroning[brewer_id] = {
                'topic': topic,
                'brew': brew,
                'config': brewer_config
            }

            # We don't want to use self.topic here as it may be a
            # wild card, and our brew may depend on the literal topic
            # of information.
            brew.start_patron(self.patron_id,
                              topic,
                              brewer_id,
                              brewer_config,
                              brewer_brew,
                              self._handle_callback)

            self.logger.info("Started patron for {}:{}".format(
                topic, brewer_id
            ))

    def remove_brewer(self, brewer_id):
        with self.topic_lock:
            if brewer_id in self.patroning:
                patron = self.patroning[brewer_id]

                patron['brew'].stop_patron(self.patron_id,
                                           patron['topic'],
                                           brewer_id)

                del(self.patroning[brewer_id])

                self.logger.info("Stopped patron for {}:{}".format(
                    patron['topic'], brewer_id
                ))

    def _handle_callback(self, brewer_id, data):
        brewer_config = self.patroning[brewer_id]['config']
        if self.crypto and 'cipher' in brewer_config:
            try:
                if brewer_id not in self.ciphers:
                    self.ciphers[brewer_id] = PubCrypto(
                        brewer_config['cipher']['mode'],
                    )

                cipher = self.ciphers[brewer_id]
                self.callback(cipher.decrypt(
                    unhexlify(brewer_config['cipher']['key'].encode()),
                    data
                ))
            except:
                self.logger.exception("Unable to decrypt data")
        else:
            self.callback(data)
