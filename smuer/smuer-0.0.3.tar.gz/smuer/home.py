#coding=utf-8
#-*-coding:utf-8-*-
#!/usr/bin/env python3


#访问的是数字海大页面


import requests
import re


#访问登录页面获取两个动态参数以及cookie
#这两个动态参数的值藏在登录页面的html里面
#故利用正则匹配出来
class First_request(object):

    def __init__(self):
        URL = 'https://cas.shmtu.edu.cn/cas/login?service=https%3A%2F%2Fportal.shmtu.edu.cn%2Fnode'
        self.url = URL
        self.content = requests.get(URL).text

    def get_lt(self):
        content = self.content
        reg = r'<input type="hidden" name="lt" value="(.*)" />'
        pattern = re.compile(reg)
        result = pattern.findall(content)
        lt = result[0]
        return lt


    def get_execution(self):
        content = self.content
        reg = r'<input type="hidden" name="execution" value="(.*?)" />'
        pattern = re.compile(reg)
        result = pattern.findall(content)
        execution = result[0]
        return execution


    def get_cookie(self):
        r = requests.get(self.url)
        return r.headers['Set-Cookie'].split(';')[0]


#利用第一次请求获取到的参数和cookie post上去
#然后分析响应头，获取location参数的值和cookie
class Second_request(object):

    def __init__(self, username=None, password=None):
        url = 'https://cas.shmtu.edu.cn/cas/login'
        r1 = First_request()
        lt = r1.get_lt()
        execution = r1.get_execution()
        login_cookie = r1.get_cookie()
        data = {'execution': execution,
                'username': username,
                'password': password,
                'lt': lt,
                '_eventId': 'submit',
                'signin': '登录'
               }
        headers = {'Cookie': login_cookie}
        payload = {"service": "https://portal.shmtu.edu.cn/node"}
        
        #因为requests.post会自动重定向，所以此处设置allow_redirects=False
        r = requests.post(url,
                          headers=headers,
                          data=data,
                          params=payload,
                          allow_redirects=False,)
        self.headers = r.headers

    def get_location(self):
        try:
            return self.headers['Location']
        except Exception as e:
            print(e)
            print("failed to get 'location' , please check your username and password ")
    def get_cookie(self):
        return self.headers['Set-Cookie'].split(';')

#利用第二步获取的参数继续访问
class Third_request(object):

    def __init__(self, username=None, password=None):
        r = Second_request(username=username, password=password)
        url = r.get_location()
        home_r = requests.get(url)
        self.content = home_r.text


    def get_tiezi():
        pass

    def get_card_money(self):
        try:
            pattern = re.compile(r'<span class="yue">(.*?)</span><span class="unit">元</span>', re.S)
            content = self.content
            money = re.findall(pattern, content)[0]
            money_msg = u'你的一卡通余额 %s' % (money)
        except Exception as e:
            print(e)
            return "可能是网络不太好导致无法获取一卡通信息"
        return money_msg
    
    def get_book_info(self):
        pass


# class Smuer():


#     def __init__(self, username, password):
#         self.username = username
#         self.password = password
        

#     def get_card_info(self):
#         try:
#             t = Third_request()
#             info = t.get_card_money()
#         except Exception as e:
#             print(e)
#         return info



if __name__ == '__main__':
    t = Third_request(username='', password='')
    try:
        print(t.get_card_money())
    except Exception as e:
        print(e)



