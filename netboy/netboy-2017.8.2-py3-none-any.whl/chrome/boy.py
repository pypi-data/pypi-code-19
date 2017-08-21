import json
import websocket
from netboy.chrome.interface import ChromeInterface
# import falsy
#
#
# class ChromeShortException(Exception):
#     pass
#
#
# class ChromeEmptyException(Exception):
#     pass
#
#
# class ChromeECMAScriptException(Exception):
#     pass
#
#
# import asyncio as aio
#
#
# class ChromeTargetException(Exception):
#     pass


class ChromeBoy:
    def __init__(self, **kwargs):
        self._host = kwargs.get('host', 'localhost')
        self._port = kwargs.get('port', 9222)
        self._url = '%s:%d' % (self._host, self._port)
        self._socket_timeout = kwargs.get('sockettimeout', 20)
        self._browser_url = 'ws://' + self._url + '/devtools/browser'
        self._id = 0
        self._user_agent = kwargs.get('useragent')
        self._http_header = kwargs.get('httpheader')
        self._cookies = kwargs.get('cookies')
        self._load_timeout = kwargs.get('loadtimeout', 15)
        self._auto_connect = kwargs.get('auto_connect', True)
        self._tabs = {}

    def new_page(self, url, xhr=False):
        c = self.chrome()
        c.Network.enable()
        c.Page.enable()
        c.Page.navigate(url=url)
        c.wait_event("Page.frameStoppedLoading", timeout=60)
        if xhr:
            ss = '''
            var xhr = new XMLHttpRequest();
            xhr.open('GET', document.location, false);
            xhr.send(null);
            var headers = xhr.getAllResponseHeaders().toLowerCase();
            JSON.stringify({
                "title": document.title,
                "location": document.location,
                "location": {
                    "href": window.location.href,
                },
                "charset": document.charset,
                "text": document.body.innerText,
                "body": document.body.outerHTML,
                "head": document.head.outerHTML,
                "xhr": {
                    "headers": headers,
                    "status": xhr.status,
                    "responseXML": xhr.responseXML,
                    "responseType": xhr.responseType,
                    "response": xhr.response,
                }
            });
            '''
        else:
            ss = '''
            JSON.stringify({
                "title": document.title,
                "location": document.location,
                "location": {
                    "href": window.location.href,
                },
                "charset": document.charset,
                "text": document.body.innerText,
                "body": document.body.outerHTML,
                "head": document.head.outerHTML,
            });
            '''
        r = c.Runtime.evaluate(expression=ss)
        c.wait_event("Network.responseReceived", timeout=60)
        r = r['result']['result']['value']
        r = json.loads(r)
        self._tabs[c]=1
        return r, c

    def chrome(self):
        self.browser = websocket.create_connection(self._browser_url, timeout=self._socket_timeout)
        return ChromeInterface(self.browser, self._host, self._port)

    def close(self):
        for c in self._tabs.keys():
            c.close_target()
        self.browser.close()


if __name__ == '__main__':
    a = ChromeBoy()
    r, c = a.new_page('http://www.bing.com')
    print(r.keys())
    r, c = a.new_page('http://www.douban.com')
    print(r.keys())
    a.close()
