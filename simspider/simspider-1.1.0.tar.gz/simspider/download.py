from urllib import request
import warnings
try:
    from chardet import detect
except:
    warnings.warn("请安装chardet库以更好的解码网页...")
    detect = lambda x: None


class Downloader:
    """
        下载器
        函数：
            down(url, encoding="utf-8", data=None, headers={}, method=None): 通过url下载网页并将其返回 
    """

    def __init__(self): pass

    def down(self, url, encoding=None, data=None, headers={}, method=None):
        htmlbytes = request.urlopen(request.Request(
            url, data, headers, method)).read()
        deo = detect(htmlbytes)
        if not encoding and not deo:
            encoding = "utf-8"
        elif deo:
            encoding = detect(htmlbytes)['encoding']
        return htmlbytes.decode(encoding, 'ignore')
