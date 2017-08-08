#coding=utf-8
#-*-coding:utf-8-*-
#!/usr/bin/env python3
from .home import Third_request
from .courses import get_table
from .grade import get_grade_table, calculate_grade


class Smuer(object):
    """docstring for Smuer"""
    def __init__(self, **kw):

        super(Smuer, self).__init__()
        self.kw = kw
        try:
            self.username = self.kw['username']
        except Exception as e:
            print(e)
            print('username could not be blank')
        try:
            self.password = self.kw['password']
        except Exception as e:
            print(e)
            print('password could not be blank')

    def get_card_info(self, **kw):

        t = Third_request(username=self.username, password=self.password)
        try:
            return t.get_card_money()

        except Exception as e:
            print(e)

    def get_courses_table(self, semester_id):

        table = get_table(semester_id=semester_id,
                          username=self.username,
                          password=self.password
                        )
        return table

    def get_grade_table(self, semester_id):

        table = get_grade_table(semester_id=semester_id,
                          username=self.username,
                          password=self.password
                        )
        return table

    def calculate_grade(self, *semester_id):
        
        average = calculate_grade(*semester_id, username=self.username, password=self.password)
        return average

    def get_active_tiezi(self, **kw):

        r = Third_request(username=self.username, password=self.password)
        return r.get_tiezi()
        
    def get_library_info():
        pass


if __name__ == '__main__':
    from password import my_password, my_username
    s = Smuer(password=my_password,
              username=my_username)
    # print(s.get_courses_table(1))
    print(s.get_active_tiezi())
    print(s.calculate_grade(1))


