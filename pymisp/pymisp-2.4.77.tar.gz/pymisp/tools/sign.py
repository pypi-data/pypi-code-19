#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    # pyme renamed to gpg the 2016-10-28
    import gpg
    from gpg.constants.sig import mode
    has_pyme = True
except ImportError:
    # pyme renamed to gpg the 2016-10-28
    import pyme as gpg
    from pyme.constants.sig import mode
    has_pyme = True
except ImportError:
    has_pyme = False

import base64

'''
from pymisp import mispevent
from sign import MISPEventSigning

me = mispevent.MISPEvent()
me.load('../../tests/57c4445b-c548-4654-af0b-4be3950d210f.json')
s = MISPEventSigning()
me = s.sign_misp_event(me)
s.validate_misp_event(me)
'''


class MISPEventSigning():

    def __init__(self):
        if not has_pyme:
            raise Exception('pyme is required, please install: pip install --pre pyme3. You will also need libgpg-error-dev and libgpgme11-dev.')
        self.signing_fingerprint = None
        self.signing_passprase = None

    def set_signing_fingerprint(self, fingerprint, passphrase=None):
        self.signing_fingerprint = fingerprint
        self.signing_passprase = passphrase

    def sign_misp_attribute(self, attribute):
        to_sign = '{type}{category}{to_ids}{uuid}{timestamp}{comment}{deleted}{value}'.format(
            type=attribute.type, category=attribute.category, to_ids=attribute.to_ids, uuid=attribute.uuid,
            timestamp=attribute.timestamp, comment=attribute.comment, deleted=attribute.deleted, value=attribute.value)
        with gpg.Context() as c:
            signed, _ = c.sign(to_sign.encode('utf-8'), mode=mode.DETACH)
        return base64.b64encode(signed).decode('utf-8')

    def validate_misp_attribute(self, attribute):
        signed_data = '{type}{category}{to_ids}{uuid}{timestamp}{comment}{deleted}{value}'.format(
            type=attribute.type, category=attribute.category, to_ids=attribute.to_ids, uuid=attribute.uuid,
            timestamp=attribute.timestamp, comment=attribute.comment, deleted=attribute.deleted,
            value=attribute.value).encode('utf-8')
        with gpg.Context() as c:
            keys = list(c.keylist('raphael.vinot'))
            c.verify(signed_data, signature=base64.b64decode(attribute.sig), verify=keys[:1])

    def sign_misp_event(self, mispevent):
        all_sigs = ''
        to_sign = '{date}{threat_level_id}{info}{uuid}{analysis}{timestamp}'.format(
            date=mispevent.date, threat_level_id=mispevent.threat_level_id, info=mispevent.info,
            uuid=mispevent.uuid, analysis=mispevent.analysis, timestamp=mispevent.timestamp)
        with gpg.Context() as c:
            signed, _ = c.sign(to_sign.encode('utf-8'), mode=mode.DETACH)
        sig = base64.b64encode(signed).decode('utf-8')
        all_sigs += sig
        mispevent.set_all_values(sig=sig)
        for a in mispevent.attributes:
            sig = self.sign_misp_attribute(a)
            all_sigs += sig
            a.set_all_values(sig=sig)
        with gpg.Context() as c:
            signed, _ = c.sign(all_sigs.encode('utf-8'), mode=mode.DETACH)
        sig = base64.b64encode(signed).decode('utf-8')
        mispevent.set_all_values(global_sig=sig)
        return mispevent

    def validate_misp_event(self, mispevent):
        signed_data = '{date}{threat_level_id}{info}{uuid}{analysis}{timestamp}'.format(
            date=mispevent.date, threat_level_id=mispevent.threat_level_id, info=mispevent.info,
            uuid=mispevent.uuid, analysis=mispevent.analysis, timestamp=mispevent.timestamp).encode('utf-8')
        with gpg.Context() as c:
            keys = list(c.keylist('raphael.vinot'))
            c.verify(signed_data, signature=base64.b64decode(mispevent.sig), verify=keys[:1])
        for a in mispevent.attributes:
            self.validate_misp_attribute(a)
        all_sigs = ''
        all_sigs += mispevent.sig
        for a in mispevent.attributes:
            all_sigs += a.sig
        all_sigs = all_sigs.encode('utf-8')
        with gpg.Context() as c:
            keys = list(c.keylist('raphael.vinot'))
            c.verify(all_sigs, signature=base64.b64decode(mispevent.global_sig), verify=keys[:1])
