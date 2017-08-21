"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.protocol import PubkeeperProtocol
from pubkeeper.protocol.packet import *  #noqa


class PubkeeperServerProtocol(PubkeeperProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handlers.update({
            Packet.CLIENT_AUTHENTICATE: self.on_client_authenticate,
            Packet.BREWER_REGISTER: self.on_brewer_register,
            Packet.BREWER_UNREGISTER: self.on_brewer_unregister,
            Packet.PATRON_REGISTER: self.on_patron_register,
            Packet.PATRON_UNREGISTER: self.on_patron_unregister,
            Packet.BREWS_REGISTER: self.on_brews_register,
            Packet.SEGMENT_REGISTER: self.on_segment_register
        })

    def on_client_authenticate(self, token):
        """on_client_authenticate

        Called when a CLIENT_AUTHENTICATE packet is received

        Args:
            token (string) - Issued JWT
        """
        raise NotImplementedError()

    def on_brewer_register(self, topic, brewer_id, brewer_config, brews):
        """on_brewer_register

        Called when a BREWER_REGISTER packet is received

        Args:
            topic (string) - Topic of publication.  This may not be wildcarded.
            brewer_id (uuid) - UUID of Brewer
            brewer_config (dict) - Any configuration that the brewer
                                   has (eg. crypto)
            brews (list) - Set of potential transport for the given brewer
        """
        raise NotImplementedError()

    def on_brewer_unregister(self, topic, brewer_id):
        """on_brewer_unregister

        Called when a BREWER_UNREGISTER packet is received

        Args:
            topic (string) - Topic used for registeration of brewer
            brewer_id (uuid) - UUID of Brewer
        """
        raise NotImplementedError()

    def on_patron_register(self, topic, patron_id, brews):
        """on_patron_register

        Called when a PATRON_REGISTER packet is received

        Args:
            topic (string) - Topic of subscription
            patron_id (uuid) - UUID of Patron
            brews (list) - Set of potential transport for the given patron
        """
        raise NotImplementedError()

    def on_patron_unregister(self, topic, patron_id):
        """on_patron_unregister

        Called when a PATRON_UNREGISTER packet is received

        Args:
            topic (string) - Topic used for patron subscription
            patron_id (uuid) - UUID of Patron
        """
        raise NotImplementedError()

    def on_brews_register(self, brews, bridge_mode):
        """on_brews_register

        Called when a BREWS_REGISTER packet is received

        Args:
            brews (list) - Set of brews/transports supported by client
            bridge_mode (bool) - Specifies if client can serve as a bridge
        """
        raise NotImplementedError()

    def on_segment_register(self, segment_id, brewer_brew, patron_brew):
        """on_segment_unregister

        Called when a PATRON_UNREGISTER packet is received

        Args:
            segment_id (uuid) - segment UUID
            brewer_brew (dict) - segment-created-brewer brew information
            patron_brew (dict) - segment-created-patron brew information
        """
        raise NotImplementedError()
