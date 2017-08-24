import argparse
import sys
import os
import datetime
import random
import hashlib
import urllib.parse
import requests

try:
    from utils import ask, str_compat
except ModuleNotFoundError:
    from pelicantool.utils import ask, str_compat

try:
    sys.path.append(os.getcwd())
    import pelicanconf
except ModuleNotFoundError:
    sys.path.append(os.path.join(os.getcwd(), 'tests'))
    import pelicanconf

__version__ = '0.1.0'


class Article(object):
    def __init__(self):
        self._title = ''
        self._date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._modified = self._date
        self._tags = ' '
        self._author = pelicanconf.AUTHOR
        self._format = '.md'
        self._filename = None

    def translation(self, query, from_='zh', to='en'):
        '''
        请求百度翻译 api 获取翻译结果
        '''
        appid = '20161217000034172'
        secretKey = '07Qh2zEwKIx3kGwer1Uz'
        salt = random.randint(32768, 65536)
        sign = appid + query + str(salt) + secretKey
        m1 = hashlib.md5(sign.encode('utf8'))
        sign = m1.hexdigest()
        url = 'http://api.fanyi.baidu.com/api/trans/vip/translate?'
        url = url + urllib.parse.urlencode(
            {'q': query, 'from': from_, 'to': to, 'appid': appid,
             'salt': salt, 'sign': sign})

        r = requests.get(url)
        r.encoding = 'utf-8'
        result = r.json()
        if 'error_code' in result:
            return None

        if 'trans_result' in result:
            return result['trans_result'][0].get('dst', None)

        return None

    def create(self, expath=None):
        '''
        create article
        args:
            expath: 文件存储目录， 若为None，则根据 pelicanconf.py 中的 PATH 来自动判断
        '''
        print("start creating...")
        if self.title:
            content = '\n'.join(self.content)
            if self._create_file(self.filename, content, expath):
                print("{fullname} craete ....... [successful!]\n".format(
                    fullname=self.filename))
                print('\n'.join(self.content))
            else:
                print("failed!")

    @property
    def filename(self):
        '''
        将要生成的文件名
        '''
        if self._filename is None:
            self._filename = '{time}-{title}{format}'.format(
                time=datetime.datetime.now().strftime('%Y-%m-%d'),
                title=self.title,
                format=self.format)

        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value

    def _create_file(self, fullname, content, expath=None):
        # 目录不存在,则创建
        if expath is not None:
            path = expath
        else:
            path = pelicanconf.PATH
        if os.path.isdir(path) is False:
            print("目录不存在,创建中...........创建完成")
            os.makedirs(os.path.join(path))

        fullname = os.path.join(path, fullname)

        with open(fullname, 'w') as fp:
            fp.write(content)

        return True

    @property
    def content(self):
        '''
        create content
        '''
        content = list()
        content = list()
        content.append(self.title)
        content.append(len(self.title) * '==' + '\n')
        content.append(':date: ' + self.date)
        content.append(':modified: ' + self.modified)
        content.append(':slug: ' + self.slug)
        if self.tags:
            content.append(':tags: ' + self.tags)
        content.append(':author: ' + self.author)
        content.append('\n')

        return content

    @property
    def format(self):
        return self._format

    @format.setter
    def format(self, value):
        format_ = ('.md', '.rst')
        if value in format_:
            self._format = value

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        self._date = value

    @property
    def modified(self):
        return self._modified

    @modified.setter
    def modified(self, value):
        self._modified = value

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, value):
        self._tags = value

    @property
    def slug(self):
        self._slug = self.translation(self.title)
        if isinstance(self._slug, str):
            self._slug = self._slug.replace(' ', '_')
            return self._slug
        return None

    @slug.setter
    def slug(self, value):
        self._slug = value

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, value):
        self._author = value

    def __str__(self):
        data = {'title': self.title,
                'date': self.date,
                'modified': self.modified,
                'tags': self.tags,
                'slug': self.slug,
                'author': self.author,
                'format': self.format}
        return str(data)


def main():
    parser = argparse.ArgumentParser(
        prog='pelicantool',
        description='A auto tool for Pelican',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--version',
                        action='version', version='%(prog)s 2.0')
    # args = parser.parse_args()

    print('''Welcome to pelicantool v{v}.

This script helps you create new articles.

Please answer the following questions so this script can generate the

information needed by article.

    '''.format(v=__version__))
    article = Article()
    article.title = ask('What will be the title of this article?',
                        answer=str_compat)
    article.tags = ask('Tags，use , split:',
                       answer=str_compat, default=article.tags)
    article.slug = ask('Slug:', answer=str_compat, default=article.slug)
    article.author = ask('Author:', answer=str_compat, default=article.author)
    article.date = ask('Date:', answer=str_compat, default=article.date)
    confirm = ask('Confirm creation?', bool, True)

    if confirm:
        article.create()


if __name__ == '__main__':
    main()
