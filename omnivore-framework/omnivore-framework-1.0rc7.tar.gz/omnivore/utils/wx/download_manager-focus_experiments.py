""" Download manager using background threads
"""
import os
import time
import urllib2
import tempfile

import wx
import wx.lib.scrolledpanel as scrolled

from omnivore.utils.background_http import BaseRequest, BackgroundHttpMultiDownloader

import logging
log = logging.getLogger(__name__)


class NoCallback(object):
    def __call__(self):
        def no_callback(req):
            print "no callback for", req
            return
        return no_callback


class DownloadURLRequest(BaseRequest):
    blocksize = 64 * 1024

    debug = False

    def __init__(self, url, path, threadsafe_progress_callback=None, finished_callback=None):
        BaseRequest.__init__(self)
        self.url = url
        self.is_skippable = False
        self.expected_size = 0
        self.size = 0
        self.wants_cancel = False
        self.is_cancelled = False
        self.path = path
        self._threadsafe_progress_callback = None
        self._finished_callback = None
        self.threadsafe_progress_callback = threadsafe_progress_callback
        self.finished_callback = finished_callback

    @property
    def threadsafe_progress_callback(self):
        return self._threadsafe_progress_callback

    @threadsafe_progress_callback.setter
    def threadsafe_progress_callback(self, callback):
        if callback is not None:
            self._threadsafe_progress_callback = callback
        else:
            self._threadsafe_progress_callback = NoCallback()()

    @property
    def finished_callback(self):
        return self._finished_callback

    @finished_callback.setter
    def finished_callback(self, callback):
        if callback is not None:
            self._finished_callback = callback
        else:
            self._finished_callback = NoCallback()()

    def __str__(self):
        if not self.is_started:
            return "%s download pending" % (self.url)
        elif self.is_finished:
            if self.error is None:
                if self.data:
                    return "%d bytes in %s" % (self.size, self.path)
                elif self.is_cancelled:
                    return "%s cancelled, %d of %d bytes" % (self.url, self.size, self.expected_size)
                else:
                    return "%s incomplete download, %d of %d bytes" % (self.url, self.size, self.expected_size)
            else:
                return "%s error: %s" % (self.url, self.error)
        else:
            return "%s downloading, %d/%d" % (self.url, self.size, self.expected_size)

    def cancel(self):
        self.wants_cancel = True

    def get_data_from_server(self):
        try:
            request = urllib2.Request(self.url)
            response = urllib2.urlopen(request)
            headers = response.info()
            if "Content-Length" in headers:
                self.expected_size = int(headers['Content-Length'])
            finished = False
            tmp_path = self.path + ".download"
            with open(tmp_path, 'wb') as fh:
                while True:
                    chunk = response.read(self.blocksize)
                    if not chunk:
                        finished = True
                        break
                    if self.wants_cancel:
                        self.is_cancelled = True
                        break
                    fh.write(chunk)
                    self.size += len(chunk)
                    self.threadsafe_progress_callback(self)
                    if self.debug:
                        time.sleep(.1)
            if finished:
                try:
                    os.remove(self.path)
                except OSError:
                    pass
                os.rename(tmp_path, self.path)
                self.data = self.path
            self.finish()

        except (urllib2.URLError, ValueError, OSError), e:
            self.handle_error(e)

    def handle_error(self, e):
        self.error = e
        self.finish()

    def finish(self):
        self.is_finished = True
        self.threadsafe_progress_callback(self)
        self.threadsafe_progress_callback = None
        wx.CallAfter(self.finished_callback, self, self.error)
        self.finished_callback = None

    def get_gauge_value(self):
        if self.expected_size == 0:
            return -1
        return self.size * 100 / self.expected_size


class RequestStatusControl(wx.Panel):
    border = 5

    def __init__(self, parent, req, **kwargs):
        wx.Panel.__init__(self, parent, -1, **kwargs)
        self.req = req
        hbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(hbox)
        self.text = wx.StaticText(self, -1, req.url, style=wx.ST_ELLIPSIZE_START)
        hbox.Add(self.text, 0, flag=wx.EXPAND|wx.ALL, border=self.border)
        vbox = wx.BoxSizer(wx.HORIZONTAL)
        self.gauge = wx.Gauge(self, -1)
        self.gauge.SetRange(100)
        vbox.Add(self.gauge, 1, flag=wx.EXPAND|wx.ALL)
        self.cancel = wx.Button(self, -1, "Cancel")
        self.cancel.Bind(wx.EVT_BUTTON, self.on_cancel)
        vbox.Add(self.cancel, 0, flag=wx.EXPAND|wx.LEFT, border=self.border)
        hbox.Add(vbox, 0, flag=wx.EXPAND|wx.ALL, border=self.border)
        hbox.Fit(self)
        self.Layout()

    def on_cancel(self, evt):
        self.req.cancel()

    def update(self):
        self.text.SetLabel(str(self.req))
        perc = self.req.get_gauge_value()
        if perc == -1:
            self.gauge.Pulse()
        else:
            self.gauge.SetValue(perc)
        if self.req.is_finished:
            self.cancel.Enable(False)


class NoFocusButton(wx.lib.buttons.GenButton):
    def __init__(self, parent, id=wx.ID_ANY, label=wx.EmptyString, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, validator=wx.DefaultValidator, name=wx.ButtonNameStr):
        wx.lib.buttons.GenButton.__init__(self,parent,id,label,pos,size,style,validator,name)
    def AcceptsFocusFromKeyboard(self):
        return False # does not accept focus
    def AcceptsFocus(self):
        return False # does not accept focus

BUFFERED = 0
class GenStaticText(wx.PyControl):
    labelDelta = 1

    def __init__(self, parent, ID=-1, label="",
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0,
                 name="genstattext"):
        wx.PyControl.__init__(self, parent, ID, pos, size, style|wx.NO_BORDER,
                             wx.DefaultValidator, name)

        wx.PyControl.SetLabel(self, label) # don't check wx.ST_NO_AUTORESIZE yet
        self.InheritAttributes()
        self.SetInitialSize(size)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        if BUFFERED:
            self.defBackClr = self.GetBackgroundColour()
            self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        else:
            self.SetBackgroundStyle(wx.BG_STYLE_SYSTEM)
            


    def SetLabel(self, label):
        """
        Sets the static text label and updates the control's size to exactly
        fit the label unless the control has wx.ST_NO_AUTORESIZE flag.
        """
        wx.PyControl.SetLabel(self, label)
        style = self.GetWindowStyleFlag()
        self.InvalidateBestSize()
        if not style & wx.ST_NO_AUTORESIZE:
            self.SetSize(self.GetBestSize())
        self.Refresh()


    def SetFont(self, font):
        """
        Sets the static text font and updates the control's size to exactly
        fit the label unless the control has wx.ST_NO_AUTORESIZE flag.
        """
        wx.PyControl.SetFont(self, font)
        style = self.GetWindowStyleFlag()
        self.InvalidateBestSize()
        if not style & wx.ST_NO_AUTORESIZE:
            self.SetSize(self.GetBestSize())
        self.Refresh()


    def DoGetBestSize(self):
        """
        Overridden base class virtual.  Determines the best size of
        the control based on the label size and the current font.
        """
        label = self.GetLabel()
        font = self.GetFont()
        if not font:
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        dc = wx.ClientDC(self)
        dc.SetFont(font)
        
        maxWidth = totalHeight = 0
        for line in label.split('\n'):
            if line == '':
                w, h = dc.GetTextExtent('W')  # empty lines have height too
            else:
                w, h = dc.GetTextExtent(line)
            totalHeight += h
            maxWidth = max(maxWidth, w)
        best = wx.Size(maxWidth, totalHeight)
        self.CacheBestSize(best)
        return best


    def Enable(self, enable=True):
        """Overridden Enable() method to properly refresh the widget. """

        wx.PyControl.Enable(self, enable)
        self.Refresh()


    def Disable(self):
        """Overridden Disable() method to properly refresh the widget. """

        wx.PyControl.Disable(self)
        self.Refresh()

           
    def AcceptsFocus(self):
        """Overridden base class virtual."""
        return False


    def GetDefaultAttributes(self):
        """
        Overridden base class virtual.  By default we should use
        the same font/colour attributes as the native StaticText.
        """
        return wx.StaticText.GetClassDefaultAttributes()


    def ShouldInheritColours(self):
        """
        Overridden base class virtual.  If the parent has non-default
        colours then we want this control to inherit them.
        """
        return True

    
    def OnPaint(self, event):
        if BUFFERED:
            dc = wx.BufferedPaintDC(self)
        else:
            dc = wx.PaintDC(self)
        width, height = self.GetClientSize()
        if not width or not height:
            return

        if BUFFERED:
            clr = self.GetBackgroundColour()
            if wx.Platform == "__WXMAC__" and clr == self.defBackClr:
                # if colour is still the default then use the theme's  background on Mac
                themeColour = wx.MacThemeColour(kThemeBrushDialogBackgroundActive)
                backBrush = wx.Brush(themeColour)
            else:
                backBrush = wx.Brush(clr, wx.SOLID)
            dc.SetBackground(backBrush)
            dc.Clear()

        if self.IsEnabled():
            dc.SetTextForeground(self.GetForegroundColour())
        else:
            dc.SetTextForeground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))
            
        dc.SetFont(self.GetFont())
        label = self.GetLabel()
        style = self.GetWindowStyleFlag()
        x = y = 0
        for line in label.split('\n'):
            if line == '':
                w, h = self.GetTextExtent('W')  # empty lines have height too
            else:
                w, h = self.GetTextExtent(line)
            if style & wx.ALIGN_RIGHT:
                x = width - w
            if style & wx.ALIGN_CENTER:
                x = (width - w)/2
            dc.DrawText(line, x, y)
            y += h


    def OnEraseBackground(self, event):
        pass



class DownloadControl(scrolled.ScrolledPanel):
    """
    View of list of downloaded items
    """

    def __init__(self, parent, downloader, path=None, prefix="downloads_", **kwargs):
        scrolled.ScrolledPanel.__init__(self, parent, -1, **kwargs)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_ALWAYS)
        self.SetupScrolling(scroll_x=False)

        panel = wx.Panel(self, -1)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.header = wx.StaticText(panel, -1, "")
        hbox.Add(self.header, 1, flag=wx.ALIGN_CENTER)

        # Adding the button prevents the window from being dismissed when in a
        # sidebar popup.
        #self.setdir = wx.Button(self, -1, "Download Dir")
        #self.setdir = NoFocusButton(self, -1, "Download Dir")
        #self.setdir.Bind(wx.EVT_BUTTON, self.on_setdir)
        self.setdir = GenStaticText(self, -1, "Download Dir")
        self.setdir.SetLabel("Download Dir")
        hbox.Add(self.setdir, 0, flag=wx.EXPAND|wx.ALL)
        panel.SetSizer(hbox)
        panel.Layout()
        panel.Fit()

        sizer.Add(hbox, 0, flag=wx.EXPAND)

        self.SetSizer(sizer)
        sizer.Layout()
        self.Fit()

        self.default_path = path
        self.dir_prefix = prefix
        self.downloader = downloader
        self.req_map = {}
        self.update_header()

        # self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.setdir.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        # # self.Bind(wx.EVT_KILL_FOCUS, self.on_lose_focus)
        # self.Bind(wx.EVT_CHAR, self.on_focus)
        # self.Bind(wx.EVT_CHAR_HOOK, self.on_focus)
        # self.Bind(wx.EVT_CHILD_FOCUS, self.on_child_focus)
        #wx.CallAfter(self.request_download, 'http://playermissile.com', "index.html", lambda a,b:None)
        self.Bind(wx.EVT_NAVIGATION_KEY, self.on_navigation_key)

    @property
    def path(self):
        if self.default_path:
            return default_path
        return tempfile.mkdtemp(prefix=self.dir_prefix)

    @path.setter
    def path(self, value):
        if value:
            self.default_path = value

    @property
    def num_active(self):
        count = 0
        for req in self.req_map.keys():
            if not req.is_finished:
                count += 1
        return count

    def update_header(self):
        count = self.num_active
        if count == 0:
            text = "No active downloads"
        elif count == 1:
            text = "1 active download"
        else:
            text = "1 active download, %d queued" % (count - 1)
        self.header.SetLabel(text)

    def request_download(self, url, filename, callback):
        if not os.path.isabs(filename):
            filename = os.path.normpath(os.path.join(self.path, filename))
        log.debug("request_download: %s" % filename)
        req = DownloadURLRequest(url, filename, finished_callback=callback)
        self.add_request(req)
        return req

    def add_request(self, req):
        rc = RequestStatusControl(self, req)
        req.threadsafe_progress_callback = self.threadsafe_progress_callback
        self.req_map[req] = rc
        sizer = self.GetSizer()
        sizer.Add(rc, 0, flag=wx.EXPAND)
        self.Layout()
        self.SetupScrolling()
        self.downloader.send_request(req)

    def threadsafe_progress_callback(self, req):
        rc = self.req_map[req]
        wx.CallAfter(rc.update)
        wx.CallAfter(self.update_header)

    def on_setdir(self, evt):
        dlg = wx.DirDialog(self, "Choose the download directory:", style=wx.DD_DEFAULT_STYLE)
        dlg.SetPath(self.path)
        if dlg.ShowModal() == wx.ID_OK:
            self.path = dlg.GetPath()
        dlg.Destroy()

    def on_key_down(self, evt):
        key = evt.GetKeyCode()
        log.debug("evt=%s, key=%s" % (evt, key))
        evt.Skip()

    def on_navigation_key(self, evt):
        log.debug("on_navigation_key!")
        #self.SetFocus()
        #evt.Skip()

    def on_focus(self, evt):
        log.debug("on_focus!")
        #self.SetFocus()
        #evt.Skip()

    def on_lose_focus(self, evt):
        log.debug("on_lose_focus!")
        evt.Skip()

    def on_child_focus(self, evt):
        log.debug("on_child_focus!")
        evt.Skip()

if __name__ == "__main__":
    # Due to the package import in the parent directory, running from this
    # directory won't work. Have to hack it:
    #
    # PYTHONPATH=../../.. python download_manager.py
    from omnivore.utils.background_http import BackgroundHttpDownloader
    import wx.lib.inspection

    class MyFrame(wx.Frame):
        def __init__(self, parent, id, title):
            wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.DefaultSize)
            self.dlcontrol = DownloadControl(self, None)

    class MyApp(wx.App):
        def OnInit(self):
            self.dlframe = MyFrame(None, -1, 'Download Manager')
            self.dlframe.Show(True)
            self.dlframe.Centre()
            return True

    def finished_callback(req, error):
        print "FINISHED!", req

    def do_download(dlc):
        req = dlc.request_download('http://playermissile.com', "index.html", finished_callback)
        req2 = dlc.request_download('http://playermissile.com/mame', "mame-index.html", finished_callback)
        req3 = dlc.request_download('http://playermissile.com/jumpman', "jumpman-index.html", finished_callback)
        req4 = dlc.request_download('http://playermissile.com/jumpman', "jumpman-index.html", finished_callback)
        req5 = dlc.request_download('http://playermissile.com/jumpman', "jumpman-index.html", finished_callback)

    app = MyApp(0)
    downloader = BackgroundHttpDownloader()
    app.dlframe.dlcontrol.downloader = downloader
    dlc = app.dlframe.dlcontrol
    DownloadURLRequest.blocksize = 1024
    wx.CallAfter(do_download, dlc)
    inspect = wx.lib.inspection.InspectionTool()
    wx.CallAfter(inspect.Show)

    app.MainLoop()

    downloader = None
