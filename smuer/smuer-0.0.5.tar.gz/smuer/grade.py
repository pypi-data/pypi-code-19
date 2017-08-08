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

    def __init__(self, username=None, password=None, which_semester=None):
        semester_id = 75+20*(which_semester-1)
        url = 'http://jwxt.shmtu.edu.cn/shmtu/teach/grade/course/person!search.action?semesterId=%s&projectType=' % (semester_id)
        try:
            r = Third_request(username=username, password=password)
            headers = {'Cookie': r.get_cookie()}
            r = requests.post(url, headers=headers)
            self.headers = r.headers
            self.content = r.text
        except Exception as e:
            print(e)

    def get_text(self):
        return self.content
    # print(self.content)

    def get_headers(self):
        return self.headers

    def get_cookie(self):
        return self.headers['Set-Cookie']


class Table(object):
    def __init__(self, username=None, password=None, which_semester=None):
        f = Fourth_request(username=username, password=password, which_semester=which_semester)
        text = f.get_text()
        text = text.replace('\n', 'V').replace('\t', 'V').replace(' ', 'V')

        pattern = r'<tr>VV<td>(.*?)V(.*?)</td>VVV<td>(.*?)</td>VVV<td>(.*?)</td>VVV<td>(.*?)</td>VVV<td>(.*?)</td>VVV<td>(.*?)</td>VVV<td>(.*?)</td>V<tdV(.*?)>VVVVVVVV(.*?)VV</td>VVVVVVVV<td>(.*?)</td>V<tdV(.*?)>VVV(.*?)V</td><td>VVV(.*?)V</td>VVV</tr>'
        r = re.compile(pattern)
        result = r.findall(text)
        self.table = result

    def get_table(self):
        return self.table

class Handle_row(object):

    def __init__(self, row):
        self.row = row
    def get_year(self):
        return self.row[0]
    def get_semester(self):
        return self.row[1]
    def get_id(self):
        return self.row[2]
    def get_order(self):
        return self.row[3]
    def get_name(self):
        return self.row[4]
    def get_type(self):
        return self.row[5]
    def get_kind(self):
        return self.row[6]
    def get_credit(self):
        return self.row[7]
    def get_status(self):
        return self.row[10]
    def get_result(self):
        return self.row[12]
    def get_point(self):
        return self.row[13]




class Calculate(object):
    def __init__(self, username=None, password=None, which_semester=None):
        t = Table(username=username, password=password, which_semester=which_semester)
        table = t.get_table()
        #总学分
        credit_sum = 0
        #总的（学分*绩点）
        cp_sum = 0
        for row in table:
            r = Handle_row(row)
            credit = float(r.get_credit())
            point = float(r.get_point())
            cp_sum += credit*point
            credit_sum += credit
        self.cp_sum = cp_sum
        self.credit_sum = credit_sum
        try:
            self.average_point = cp_sum/credit_sum
        except Exception as e:
            print(e)
            print("")
    def get_cp_sum(self):
        return self.cp_sum
    def get_average_point(self):
        return self.average_point
    def get_credit_sum(self):
        return self.credit_sum

def construct_dict(**kw):
    return kw

def get_grade_table(username, password, semester_id=None):
    t = Table(username=username,
              password=password,
              which_semester=semester_id,
              )
    raw_table = t.get_table()

    new_table = []
    for row in raw_table:
        r = Handle_row(row)
        row_dict = construct_dict(year=r.get_year(),
                                  semester_id=r.get_semester(),
                                  course_name=r.get_name(),
                                  type=r.get_type(),
                                  kind=r.get_kind(),
                                  id=r.get_id(),
                                  order=r.get_order(),
                                  credit=r.get_credit(),
                                  status=r.get_status(),
                                  point=r.get_point(),
                                  result=r.get_result()
                                  )
        new_table.append(row_dict)

    return new_table

    



def calculate_grade(*args, username=None, password=None):

    #cp : produt of (credit*point)
    semester_id_list = args
    cp_sum_list = []
    credit_sum_list = []
    for s in semester_id_list:
        c = Calculate(username=username, password=password, which_semester=s)
        cp_sum = c.get_cp_sum()
        cp_sum_list.append(cp_sum)
        credit_sum = c.get_credit_sum()
        credit_sum_list.append(credit_sum)

    total_credit = 0
    for c in credit_sum_list:
        total_credit += c
    total_cp = 0
    for cp in cp_sum_list:
        total_cp += cp
    try:
        result = total_cp/total_credit
        return round(result, 2)
    except Exception as e:
        print(e)
        return 


if __name__ == '__main__':
    
    print(calculate_grade(1,2, username='', password=''))

    # c = Caculate(username='', password='', which_semester=2)
    # #this semester
    # print(c.get_average_point())
    

    # c = Caculate(username='', password='', which_semester=2)
    # print(c.get_average_point())

    # this_year_ave = caculate_more_average(username='', password='', semester_id_list=[1,2])
    # print(this_year_ave)