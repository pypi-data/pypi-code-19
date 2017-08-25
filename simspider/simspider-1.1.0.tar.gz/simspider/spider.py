from copy import copy
class Spider:
    """爬行器"""
    def __init__(self):
        self.root = None
        self.downloader = None
        self.deep = 0
        self.parsers = []
        self.storagers = []
        self.test = False
        self.mult = False

    def setMult(self, maxmult=16):
        """设置为多线程下载"""
        from queue import Queue
        import asyncio
        self.mult = True
        self.urls = Queue()

    def setRoot(self, root):
        """设置网页根节点"""
        self.root = root

    def setDownloader(self, downloader):
        """设置下载器"""
        self.downloader = downloader

    def setDeep(self, deep):
        """
            设置爬取深度
        """
        self.deep = deep

    def setParsers(self, parsers):
        """
            设置解析器列表
            parsers : 解析器列表，顺序按解析深度定
        """
        self.parsers = parsers

    def setStoragers(self, storagers):
        """
            设置存储器列表
            storagers : 存储器列表
        """
        self.storagers = storagers

    def setTest(self):
        """
            设置为测试状态
        """
        self.test = True

    def __ex(self, i, url):
        """解析第n层数据并返回下层链接"""
        print('正在爬行：',url)
        parser = self.parsers[i]()
        storager = self.storagers[i]()
        html = self.downloader().down(url)
        parser.setHtml(html)
        storager.save(parser.getData())
        # 处理下一页
        nurl = parser.nextUrl()
        if self.test:
            print('Next url: '+str(nurl))
        elif nurl:
            self.__ex(i, nurl)
        # 处理下一层
        for uri in parser.nextUrls():
            if i + 1 < self.deep:
                self.__ex(i + 1, uri)
            elif self.test:
                print('Next urls: '+uri)

    def __multex(self,i,url):
        """多线程下载器"""
        pass

    def start(self):
        """开始"""
        self.__ex(0, self.root)
