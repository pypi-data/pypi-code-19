
from uiutil.window.dynamic import DynamicRootWindow, DynamicChildWindow
from .device_frame import DeviceFrame, ROOT_LAYOUT


class _DeviceWindow(object):

    def __init__(self,
                 layout_key=ROOT_LAYOUT,
                 window_title=u'Device Config',
                 *args,
                 **kwargs):
        super(_DeviceWindow, self).__init__(layout_key=layout_key,
                                            window_title=window_title,
                                            *args,
                                            **kwargs)

    def _setup(self):
        self.title(self.window_title)
        self.dynamic_frame = DeviceFrame(parent=self._main_frame,
                                         layout_key=self.key,
                                         item_dict=self.item_dict)


class DeviceRootWindow(_DeviceWindow, DynamicRootWindow):

    def __init__(self, *args, **kwargs):
        super(DeviceRootWindow, self).__init__(*args, **kwargs)


class DeviceChildWindow(_DeviceWindow, DynamicChildWindow):

    def __init__(self, *args, **kwargs):
        super(DeviceChildWindow, self).__init__(*args, **kwargs)
