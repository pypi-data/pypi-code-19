"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.protocol import PubkeeperProtocol
from pubkeeper.protocol.packet import *  #noqa


class PubkeeperClientProtocol(PubkeeperProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handlers.update({
            Packet.CLIENT_AUTHENTICATED: self.on_client_authenticated,
            Packet.BREWER_NOTIFY: self.on_brewer_notify,
            Packet.BREWER_REMOVED: self.on_brewer_removed,
            Packet.PATRON_NOTIFY: self.on_patron_notify,
            Packet.PATRON_REMOVED: self.on_patron_removed,
            Packet.SEGMENT_CREATE: self.on_segment_create,
            Packet.SEGMENT_DESTROY: self.on_segment_destroy,
            Packet.SEGMENT_CONNECT_BREWER: self.on_segment_connect_brewer
        })

    def on_client_authenticated(self, authenticated):
        """on_client_authenticated

        Called when a CLIENT_AUTHENTICATED packet is received

        Args:
            authenticated (bool) - Authenticated state
        """
        raise NotImplementedError()

    def on_brewer_notify(self, patron_id, brewers):
        """on_brewer_notify

        Called when a BREWER_NOTIFY packet is received

        Args:
            patron_id (uuid) - UUID of the clients patron subscribing
            brewers (list) - List of brewers.  On initial patron registration
                this will contain a list of all of the brewers of the given
                topic.  Subsiquently, as new brewers join the network, the
                list will contain a single element of the new brewer.  The
                contents of the list will be a dictionary containing a:
                    topic (string) - Topic of publication
                    brewer_id (uuid) - UUID of the network brewer brewing
                    brewer_config (dict) - Any configuration that the brewer
                                           has (eg. crypto)
                    brew (dict) - Brew configuration options
        """
        raise NotImplementedError()

    def on_brewer_removed(self, topic, patron_id, brewer_id):
        """on_brewer_removed

        Called when a BREWER_REMOVED packet is received

        Args:
            topic (string) - Topic of publication
            patron_id (uuid) - UUID of the clients patron subscribing
            brewer_id (uuid) - UUID of the network brewer brewing
        """
        raise NotImplementedError()

    def on_patron_notify(self, brewer_id, patrons):
        """on_patron_notify

        Called when a PATRON_NOTIFY packet is received

        Args:
            brewer_id (uuid) - UUID of the clients brewer brewing
            patrons (list) - List of patrons.  On initial patron registration
                this will contain a list of all of the patrons of the given
                topic.  Subsiquently, as new patrons join the network, the
                list will contain a single element of the new patrons.  The
                contents of the list will be a dictionary containing a:
                    topic (string) - Topic of publication
                    patron_id (uuid) - UUID of the network patron brewing
                    brew (dict) - Brew configuration options
        """
        raise NotImplementedError()

    def on_patron_removed(self, topic, brewer_id, patron_id):
        """on_patron_removed

        Called when a PATRON_REMOVED packet is received

        Args:
            topic (string) - Topic of subscription
            brewer_id (uuid) - UUID of the clients brewer brewing
            patron_id (uuid) - UUID of the network patron subscribing
        """
        raise NotImplementedError()

    def on_segment_create(self, segment_id, topic,
                          brewer_details, patron_details):
        """on_segment_create

        Called when a segment needs to be created

        Args:
            segment_id (uuid) - segment UUID
            topic (str) - segment topic
            brewer_details (dict) - dict containing brewer topic, brewer brew
                and brewer_id
            patron_details (dict) - dict containing patron topic, patron brew
                and patron_id
        """
        raise NotImplementedError()

    def on_segment_connect_brewer(self, segment_id, patron_id, patron_brew):
        """on_segment_connect_brewer

        Called to connect a brewer created in the segment once patron it
        connects to becomes available

        Args:
            segment_id (uuid) - segment UUID
            patron_id (uuid) - patron UUID
            patron_brew (dict) - patron brew information
        """
        raise NotImplementedError()

    def on_segment_destroy(self, segment_id):
        """on_segment_destroy

        Called when a segment needs to be destroyed

        Args:
            segment_id (uuid) - segment UUID
        """
        raise NotImplementedError()
