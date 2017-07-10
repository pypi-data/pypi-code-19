# -*- coding: utf-8 -*-
__author__ = 'XaviTorello'

class oKW_Queue (object):
    """
    Queue model

    A queue is composed by
        * name (ip address / host)
        * port
        * db
        * collection
        * source_type

    """

    __slots__ = ('host', 'port', 'name', 'type')

    def __init__(self, host, port, name):
        """
        Set the main properties of a generic datasource
        """

        assert type(host) == str, "Host must be a string"
        assert host != "", "Host can't be empty"
        assert type(port) == int, "Port must be an integer"
        assert 1 <= port <= 65535, "Port '{}' is not inside the expected port range".format(port)
        assert type(name) == str, "Queue name must be a string"
        assert name != "", "Queue name can't be empty"

        self.host = host
        self.port = port
        self.name = name
        self.type = 'generic'


    @property
    def hostname(self):
        """
        Proxify the hostname
        """
        return self.host


    def __str__(self):
        """
        String representation of a connection
        """
        return "{}//{}:{}/{}".format(self.type, self.host, self.port, self.name)
