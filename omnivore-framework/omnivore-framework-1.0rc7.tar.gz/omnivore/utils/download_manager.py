""" Download manager using background threads
"""
import os
import time
import urllib2 as urllib2

import wx
import wx.lib.scrolledpanel as scrolled

from background_http import BaseRequest, BackgroundHttpMultiDownloader

import logging
log = logging.getLogger(__name__)


class DownloadURLRequest(BaseRequest):
    def __init__(self, url, path):
        BaseRequest.__init__(self)
        self.url = url
        self.is_skippable = False
#        self.blocksize = 16 * 1024
        self.blocksize = 1024
        self.expected_size = 0
        self.size = 0
        self.is_cancelled = False
        self.path = path

    def __str__(self):
        if not self.is_started:
            return "%s download not started" % (self.url)
        elif self.is_finished:
            if self.error is None:
                if self.data:
                    return "%s returned %d bytes in %s" % (self.url, self.size, self.path)
                else:
                    return "%s incomplete download, %d of %d bytes" % (self.url, self.size, self.expected_size)
            else:
                return "%s returned error: %s" % (self.url, self.error)
        else:
            return "%s downloading, %d of %d in %s" % (self.url, self.size, self.expected_size, self.path)

    def cancel(self):
        self.is_cancelled = True

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
                    if self.is_cancelled:
                        break
                    fh.write(chunk)
                    self.size += len(chunk)
                    print "size:", self.size
                    time.sleep(.1)
            if finished:
                try:
                    os.remove(self.path)
                except OSError:
                    pass
                os.rename(tmp_path, self.path)
                self.data = self.path

        except urllib2.URLError, e:
            self.error = e

        except ValueError, e:
            self.error = e

        except OSError, e:
            self.error = e


class RequestStatusControl(wx.Panel):
    border = 5

    def __init__(self, parent, req, **kwargs):
        wx.Panel.__init__(self, parent, -1, **kwargs)
        hbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(hbox)
        self.text = wx.StaticText(parent, -1, rec.url)
        hbox.Add(self.text, 0, flag=wx.EXPAND|wx.ALL, border=self.border)
        self.gauge = wx.Gauge(parent, -1)
        hbox.Add(self.gauge, 0, flag=wx.EXPAND|wx.ALL, border=self.border)
        self.cancel = wx.Button(parent, -1, "Cancel")
        hbox.Add(self.cancel, 0, flag=wx.EXPAND|wx.ALL, border=self.border)


class DownloadControl(scrolled.ScrolledPanel):
    """
    View of list of downloaded items
    """

    def __init__(self, parent, downloader, **kwargs):
        scrolled.ScrolledPanel.__init__(self, parent, -1, **kwargs)
        hbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(hbox)
        self.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_ALWAYS)
        self.SetupScrolling(scroll_x=False)
        hbox.Layout()
        self.Fit()
        self.downloader= downloader

    def add_request(self, req):
        rc = RequestStatusControl(self.GetParent(), req)
        self.GetSizer().Add(rc, 0, flag=wx.EXPAND)


if __name__ == "__main__":
    from background_http import BackgroundHttpDownloader

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

    app = MyApp(0)
    downloader = BackgroundHttpDownloader()
    app.dlframe.dlcontrol.downloader = downloader
    app.MainLoop()

    downloader = BackgroundHttpDownloader()
    # downloader.send_request(URLRequest('http://www.python.org/'))
    # downloader.send_request(URLRequest('http://www.doughellmann.com/PyMOTW/contents.html'))
    req = DownloadURLRequest('http://playermissile.com', "index.html")
    downloader.send_request(req)
    print req
    # downloader.send_request(URLRequest('http://docs.python.org/release/2.6.8/_static/py.png'))
    # downloader.send_request(URLRequest('http://image.tmdb.org/t/p/w342/vpk4hLyiuI2SqCss0T3jeoYcL8E.jpg'))
    # downloader.send_request(URLRequest('hvvttp://playermissile.com'))
    first = True
    for i in range(10):
        print "STEP", i, req
        downloaded = downloader.get_finished()
        for url in downloaded:
            print 'FINISHED:', url
        # if i > 1 and first:
        #     downloader.send_request(URLRequest('http://www.python.org/images/python-logo.gif'))
        #     downloader.send_request(URLRequest('http://www.python.org/'))
        #     downloader.send_request(URLRequest('http://www.doughellmann.com/PyMOTW/contents.html'))
        #     downloader.send_request(URLRequest('http://playermissile.com'))
        #     first = False
        if i == 5:
            req.cancel()
        time.sleep(.1)

    downloader = None
