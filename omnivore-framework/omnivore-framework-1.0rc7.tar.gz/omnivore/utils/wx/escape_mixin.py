import wx


class EscapeCancelMixin(object):
    """Segment selector for choosing which portion of the binary data to view
    """

    def register_escape_handler(self):
            self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)

    def on_char_hook(self, evt):
        if evt.GetKeyCode() == wx.WXK_ESCAPE:
            wx.CallAfter(self.task.on_hide_minibuffer_or_cancel, None)
        else:
            evt.Skip()
