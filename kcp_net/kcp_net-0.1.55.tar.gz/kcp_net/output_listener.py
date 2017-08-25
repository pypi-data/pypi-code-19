# coding: utf8

import kcp_wrapper


class OutputListener(kcp_wrapper.OutputListener):
    sock = None
    address = None

    def __init__(self, sock, address):
        kcp_wrapper.OutputListener.__init__(self)
        self.sock = sock
        self.address = address

    def call(self, data, kcp_obj):
        # print 'output:', repr(data)
        offset = 0
        while offset < len(data):
            try:
                ret = self.sock.sendto(data[offset:], self.address)
            except:
                # server直接关闭，client就会抛异常
                return -1

            offset += ret

        return 0
