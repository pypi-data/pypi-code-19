# -*- coding: utf-8 -*-

from netkit.box import Box
from collections import OrderedDict

# 如果header字段变化，那么格式也会变化
HEADER_ATTRS = OrderedDict([
    ('magic', ('i', 2037952207)),
    ('version', ('h', 0)),
    ('flags', ('h', 0)),
    ('packet_len', ('i', 0)),
    ('cmd', ('i', 0)),
    ('ret', ('i', 0)),
    ('node_id_num', ('16s', '')),
    ('conn_id_num', ('16s', '')),
    ('client_ip_num', ('16s', '')),
    ('uid', ('q', 0)),
    ('userdata', ('q', 0)),
    ('custom', ('q', 0)),
    ])


# 是否来自inner
FLAG_INNER = 0x01
# 是否IPV6
FLAG_IPV6 = 0x01 << 1


class Task(Box):
    header_attrs = HEADER_ATTRS

    def map(self, map_data):
        """
        获取对应的response
        :param : map_data
        :return:
        """
        assert isinstance(map_data, dict)

        init_data = dict(
            conn_id_num=self.conn_id_num,
            node_id_num=self.node_id_num,
        )
        init_data.update(map_data)

        return self.__class__(init_data)

    @property
    def client_ip(self):
        """
        获取字符串格式的IP地址
        对端传过来的本身就是原始的字节序的二进制流，所以不需要做任何特殊转化，直接使用即可。
        :return:
        """
        import socket
        if self.ipv6:
            return socket.inet_ntop(socket.AF_INET6, self.client_ip_num)
        else:
            # ipv4只有4个字节
            return socket.inet_ntop(socket.AF_INET, self.client_ip_num[:4])

    @client_ip.setter
    def client_ip(self, value):
        import socket

        if ':' in value:
            self.client_ip_num = socket.inet_pton(socket.AF_INET6, value)
            self.ipv6 = True
        else:
            self.client_ip_num = socket.inet_pton(socket.AF_INET, value)
            self.ipv6 = False

    @property
    def inner(self):
        """
        是否来自inner
        :return: True/False
        """
        return bool(self.flags & FLAG_INNER)

    @inner.setter
    def inner(self, value):
        if value:
            self.flags |= FLAG_INNER
        else:
            self.flags &= (~FLAG_INNER)

    @property
    def ipv6(self):
        """
        是否是ipv6
        :return: True/False
        """
        return bool(self.flags & FLAG_IPV6)

    @ipv6.setter
    def ipv6(self, value):
        if value:
            self.flags |= FLAG_IPV6
        else:
            self.flags &= (~FLAG_IPV6)

    @property
    def node_id(self):
        return self.node_id_num.encode('hex') if self.node_id_num else self.node_id_num

    @node_id.setter
    def node_id(self, value):
        self.node_id_num = value.decode('hex') if value else value

    @property
    def conn_id(self):
        return self.conn_id_num.encode('hex') if self.conn_id_num else self.conn_id_num

    @conn_id.setter
    def conn_id(self, value):
        self.conn_id_num = value.decode('hex') if value else value
