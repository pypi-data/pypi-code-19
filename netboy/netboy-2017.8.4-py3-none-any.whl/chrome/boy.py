import json
from concurrent import futures

import time
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
from netboy.util.grouper import grouper_it


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
        start = time.time()
        c = self.chrome()
        c.Network.enable()
        c.Page.enable()
        c.Page.navigate(url=url)
        c.wait_event("Page.frameStoppedLoading", timeout=60)
        end = time.time()
        if xhr:
            ss = '''
            var xhr = new XMLHttpRequest();
            xhr.open('GET', document.location, false);
            xhr.send(null);
            var headers = xhr.getAllResponseHeaders().toLowerCase();
            JSON.stringify({
                "title": document.title,
                "location": {
                    "href": window.location.href,
                    "origin": window.location.origin,
                },
                "charset": document.charset,
                "text": document.body.innerText,
                "body": document.body.outerHTML,
                "head": document.head.outerHTML,
                "url": %s
                "xhr": {
                    "headers": headers,
                    "status": xhr.status,
                    "responseXML": xhr.responseXML,
                    "responseType": xhr.responseType,
                    "response": xhr.response,
                    "url": "%s",
                    "time": %f,
                }
            });
            ''' % (url, end - start)
        else:
            ss = '''
            JSON.stringify({
                "title": document.title,
                "location": {
                    "href": window.location.href,
                    "origin": window.location.origin,
                },
                "charset": document.charset,
                "text": document.body.innerText,
                "body": document.body.outerHTML,
                "head": document.head.outerHTML,
                "url": "%s",
                "time": %f
            });
            ''' % (url, end - start)
        print(ss)
        r = c.Runtime.evaluate(expression=ss)
        c.wait_event("Network.responseReceived", timeout=60)
        r = r['result']['result']['value']
        r = json.loads(r)
        self._tabs[c] = 1
        return r, c

    def chrome(self):
        self.browser = websocket.create_connection(self._browser_url, timeout=self._socket_timeout)
        return ChromeInterface(self.browser, self._host, self._port)

    def close(self):
        for c in self._tabs.keys():
            c.close_target()
        self.browser.close()


class ConcurrentBoy:
    def __init__(self, max=4):
        self.max = max

    def run(self, data):
        d = data.get('data')
        i = data.get('info')
        results = []
        for dd in grouper_it(d, i.get('chunk_size', 10)):
            result = self._run(dd, i.get('max_workers'))
            results.extend(result)
        return results

    def _run(self, data, max_workers=4):
        results = []
        with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {}
            for i, payload in enumerate(data):
                d = {'url': payload} if type(payload) is str else payload
                # payload['chrome_id'] = i
                future_to_url[executor.submit(self.run1, d)] = d
                # future_to_url[executor.submit(self.run1_core, payload, browser, begin_time)] = payload
            for future in futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                except Exception as exc:
                    print('%r generated an exception: %s' % (url, exc))
                else:
                    # data['chrome_id'] = url['chrome_id']
                    results.append(data)
        return results

    def run1(self, payload):
        p = payload
        url = p.get('url')
        if not url:
            return None
        a = ChromeBoy(useragent=p.get('useragent'),
                      sockettimeout=p.get('sockettimeout'))
        r, c = a.new_page(url)
        a.close()
        return r

    def view(self, results, filters):
        scene = []
        for result in results:
            updated = {key: result.get(key) for key in filters}
            scene.append(updated)
        return scene


if __name__ == '__main__':
    a = ConcurrentBoy()
    r = a.run({
        'data': ['http://www.baidu.com', 'http://www.bing.com', 'http://www.facebook.com'],
        'info': {'chunk_size': 2}
    })
    print(json.dumps(a.view(r, ['title', 'location', 'time','url']), indent=2, ensure_ascii=False))
