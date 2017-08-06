#-*-coding:utf-8-*-
#coding=utf-8
#! python3

#============
#访问的是教务系统

import requests
import re


class First_request(object):

    def __init__(self, allow_redirects=None):
        URL = 'http://jwxt.shmtu.edu.cn/shmtu/home.action'
        r = requests.get(URL, allow_redirects=allow_redirects)
        self.content = r.text
        self.headers = r.headers

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
        return self.headers['Set-Cookie'].split(';')[0]

    def get_location(self):
        return self.headers['Location']

    def get_headers(self):
        return self.headers


class Second_request(object):

    def __init__(self,username=None, password=None):

        r1 = First_request(allow_redirects=True)
        lt = r1.get_lt()
        execution = r1.get_execution()
        login_cookie = r1.get_cookie()

        r2 = First_request(allow_redirects=False)
        url = r2.get_location()

        data = {'execution': execution,
                'username': ("%s") % username,
                'password': ("%s") % password,
                'lt': lt,
                '_eventId': 'submit',
                'signin': '登录'
               }
        headers = {'Cookie': login_cookie}
        
        r = requests.post(url,
                          headers=headers,
                          data=data,
                          allow_redirects=False,)
        self.headers = r.headers
        self.status_code = r.status_code

    def get_location(self):
        return self.headers['Location']

    def get_cookie(self):
        return self.headers['Set-Cookie'].split(';')

    def get_status(self):
        return self.status_code 

    def get_headers(self):
        return self.headers


class Third_request(object):

    def __init__(self, username=None, password=None):
        r = Second_request(username=username, password=password)
        url = r.get_location()
        next_r = requests.get(url)
        self.content = next_r.text
        self.headers = next_r.headers
        

    def get_text(self):
        return self.content
        # print(self.content)

    def get_headers(self):
        return self.headers

    def get_cookie(self):
        return self.headers['Set-Cookie']

class Fourth_request(object):

    def __init__(self,username=None, password=None):
        url = 'http://jwxt.shmtu.edu.cn/shmtu/home!childmenus.action?menu.id=22593&security.categoryId=1&_=1498735729376'
        r = Third_request(username=username, password=password)
        headers = {'Cookie': r.get_cookie()}
        r = requests.get(url, headers=headers)
        self.headers = r.headers
        self.content = r.text

    def get_text(self):
        return self.content
    # print(self.content)

    def get_headers(self):
        return self.headers

    def get_cookie(self):
        return self.headers['Set-Cookie']


class Course_table(object):

    def __init__(self, which_semester=None,username=None, password=None):
        r = Third_request(username=username, password=password)
        url = 'http://jwxt.shmtu.edu.cn/shmtu/courseTableForStd!courseTable.action'
        semester_id = 75+20*(which_semester-1) 
        data={'ignoreHead': '1',
              'setting.kind': 'std',
              'startWeek': '1',
              'semester.id': '%s' % (semester_id),
              'ids': '380129'}
        headers = {'Cookie': r.get_cookie()}
        r = requests.post(url, headers=headers, data=data)
        self.text = r.text
    def get_text(self):
        return self.text


class Course(object):
    """docstring for Course"""
    def __init__(self, which_semester, username=None, password=None):
        c = Course_table(which_semester=which_semester, username=username, password=password)
        text = c.get_text()

        #为什么下面这么蛋疼。因为脑抽了，习惯正则匹配前把一些乱七八糟的符号替换掉
        text = text.replace('+','*').replace('[','*')
        text = text.replace(']','*').replace('(','*')
        text = text.replace(')','*').replace('\n','*')
        text = text.replace('\t','*').replace(' ', '*')
        text = text.replace('*','Z')
        reg = r"newZTaskActivityZ(.*?)ZZZZactivity"
        pattern = re.compile(reg)
        result = pattern.findall(text)
        info_list = []
        for i in result:
            i = i.replace('Z','')
            i = i.split(',')
            last_str = i[-1]
            i.pop(-1)

            copy = last_str

            #课程在一学期中开课序列（o开始计数）
            course_order = copy.split(';')[0]
            # print(course_order)

            #匹配出课程在周几&第几节课（o开始计数）
            reg2 = r'index=(.*?)unitCount(.*?);'
            pattern = re.compile(reg2)
            time = pattern.findall(last_str)

            i.append(course_order)
            i.append(time)
            info_list.append(i)

        self.info_list = info_list

    def get_info_list(self):
            return self.info_list



class Lession():

    def __init__(self, info):
        self.info = info
        
        #序号
    def num(self):
        return self.info[0]

    def teacher(self):
        return self.info[1]
        #课程号
    def num2(self):
        return self.info[2]

    def name(self):
        return self.info[3]
        
        #课程号
    def num3(self):
        return self.info[4]

    def position(self):
        return self.info[5]

    #一学期下每周是否上课1为是0为否    
    def order(self):
        return self.info[6]
    
    #周几第几节
    def time(self):
        return self.info[7]

    
def construct_dic(**kw):

    return kw

def get_table(semester_id, username, password):
    c = Course(which_semester=semester_id, username=username, password=password)
    info_list = c.get_info_list()
    table = []
    for i in info_list:
        l = Lession(i)
        lession_dic = construct_dic(teacher=l.teacher(),
                                    name=l.name(),
                                    order=l.order(),
                                    position=l.position(),
                                    time = l.time(),
                                    num = l.num(),
                                    course_id = l.num2()
                                    )
        table.append(lession_dic)
    return table


if __name__ == '__main__':
    table = get_table(semester_id=1, username='', password='')
    print(table)




