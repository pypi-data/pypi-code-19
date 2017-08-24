
class Parser:
    """
        解析器
        函数:
            setHtml(html): 设置待解析的html文本（也可按自己需求设置解析对象）
            getData(): 从当前页面解析出需要的数据，并将解析后的数据返回
            nextUrls(): 从当前页面解析出下一层需要爬取的url列表并返回列表或迭代器
            nextUrl(): 返回下一页链接
    """
    data = {}

    def __init__(self): pass

    def setHtml(self, html):
        self.html = html

    def getData(self):
        return self.data

    def nextUrls(self):
        return []

    def nextUrl(self):
        return None
