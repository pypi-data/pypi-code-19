"""
    自动生成框架代码
"""

config = '''
"""
    配置爬行器
"""
from util import *




# 配置爬行入口url
root = "http://www.baidu.com"




# 配置下载器
downloader = MyDownloader


# 设置爬行深度
deep = 1




"""
    设置解析器列表，对于每一层页面都必须设置一个解析器
"""
parsers = [MyParser1,]




"""
    设置存储器列表，对于每一层页面都必须设置一个存储器
"""
storagers = [MyStor1,]
'''

util = '''
"""
    自定义下载器、解析器、存储器
"""
from simspider.download import Downloader
from simspider.parse import Parser
from simspider.save import Storager


class MyDownloader(Downloader):
    """
        自定义下载器，一般可用默认的下载器，若需自定义下载器则重写基类的down方法即可
    """
    def __init__(self):
        super(MyDownloader, self).__init__()


class MyParser1(Parser):
    """
        自定义解析器（一种解析方式对应一种解析器）
    """
    def __init__(self):
        super(MyParser1, self).__init__()

    def setHtml(self, html):
        # 设置待解析的html文本（也可按自己需求设置解析对象）
        pass

    def getData(self):
        # 从当前页面解析出需要的数据，并将解析后的数据返回
        pass

    def nextUrls(self):
        # 从当前页面解析出下一层需要爬取的url列表并返回列表或迭代器
        []

    def nextUrl(self):
        # 返回当前页的下一页链接
        return None



class MyStor1(Storager):
    """
        自定义数据存储器（一种存储方式对应一种存储器）
    """

    def __init__(self):
        super(MyStor1, self).__init__()

    def save(self, data):
        # 按自定义规则存储数据
        pass

'''

testconfig = '''
from util import *

# 配置测试url
url = "http://www.baidu.com"



# 配置下载器
downloader = MyDownloader



# 设置解析器
parser = MyParser1



# 设置存储器
storager = MyStor1

'''

mainc = """
from simspider.simgo import main
if __name__=="__main__":
    main()
"""


def main():
    with open('config.py', 'w', encoding='utf-8') as f:
        f.write(config)
    with open('util.py', 'w', encoding='utf-8') as f:
        f.write(util)
    with open('testconfig.py', 'w', encoding='utf-8') as f:
        f.write(testconfig)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(mainc)
