# coding: utf8

import time

import kcp_wrapper

from .log import logger
from .output_listener import OutputListener
from .timer import Timer


class Connection(object):

    output_listener_class = OutputListener

    # 检测过期
    expire_timer = None

    app = None
    address = None

    kcp_obj = None

    def __init__(self, app, address):
        self.app = app
        self.address = address

        self.expire_timer = Timer()
        self._set_expire_callback()
        self.app.events.create_conn(self)

        self.kcp_obj = self.create_kcp_obj()

    def create_kcp_obj(self):
        """
        可以继承重写
        :return:
        """
        kcp_obj = kcp_wrapper.KcpWrapper(self.app.conv)
        # kcp_obj.setNoDelay(1, 10, 2, 1)
        kcp_obj.setOutputListener(self.output_listener_class(self.app.socket, self.address).__disown__())
        # mtu * count，就是包数量。但是buf大小还是要受限udp 65535
        # kcp_obj.setWndSize(100, 100)
        kcp_obj.timer = Timer()

        return kcp_obj

    def get_now_time_ms(self):
        return int(time.time() * 1000) % 0xFFFFFFFF

    def kcp_update_and_check(self):
        """
        在send和input之后调用
        :return:
        """
        now = self.get_now_time_ms()

        # update
        self.kcp_obj.update(now)

        # 调用input，需要重新check
        interval = self.kcp_obj.check(now) - now
        if interval < 0:
            interval = 0
        self.kcp_obj.timer.set(interval / 1000.0, lambda: self.kcp_obj.update(self.get_now_time_ms()), force=True)

    def write(self, data):
        if isinstance(data, self.app.box_class):
            # 打包
            data = data.pack()
        elif isinstance(data, dict):
            data = self.app.box_class(data).pack()

        self.kcp_obj.send(data)
        self.kcp_update_and_check()

    def close(self):
        """
        直接关闭连接
        """
        self.app.remove_conn(self)
        self._on_connection_close()

    def closed(self):
        """
        连接是否已经关闭
        :return:
        """
        return not self.app.has_conn(self)

    def handle(self, message):
        """
        启动处理
        """
        self.kcp_obj.input(message)
        self.kcp_update_and_check()

        while True:
            data = self.kcp_obj.recv()

            if data:
                box = self.app.box_class()
                if box.unpack(data) > 0:
                    box._raw_data = data
                    self._on_read_complete(box)
            else:
                # 没有数据了才break
                break

    def _on_connection_close(self):
        # 链接被关闭的回调

        self._clear_expire_callback()

        self.app.events.close_conn(self)

    def _on_read_complete(self, box):
        """
        数据获取结束
        data: 原始数据
        box: 解析后的box
        """

        # 每收到一次消息，就进行一次延后
        self._set_expire_callback()

        try:
            self.app.events.handle_request(self, box)
        except Exception, e:
            logger.error('view_func raise exception. box: %s, e: %s',
                         box, e, exc_info=True)

    def _set_expire_callback(self):
        """
        注册超时的回调
        :return:
        """
        if self.app.timeout:
            # 超时了，就报错
            self.expire_timer.set(self.app.timeout, self._on_timeout)

    def _clear_expire_callback(self):
        self.expire_timer.clear()

    def _on_timeout(self):
        self.app.events.timeout_conn(self)
        self.close()

    def __repr__(self):
        return '<%s address: %s>' % (self.__class__.__name__, self.address)

