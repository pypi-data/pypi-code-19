# coding:  utf-8

from sys import exit
from random import randint

print "--------------------莫大大传奇------------------------"
print "一剑西来，千岩拱列，魔影纵横。"
print "这个时代强盗横行，山贼遍地，地痞霸道。就在人们活不下去的时候,出现了一个英雄---莫大大"
shape = int(raw_input("请输入莫大大的体型:1魁梧,2中等,3弱小> "))
team = int(raw_input("请选择加入的门派:1少林,2武当,3华山,4魔教> "))
print "莫大大决定除掉这个boss,还人们一片安宁"
print "苍天有眼,终于让莫大大遇到了boss"
class Person(object):
    def __init__(self,hp,mp):
        self.hp=hp
        self.mp=mp
    def rest(self):
        self.mp += randint(0,100)
    def heal(self):
        self.hp += randint(0,100)
    def check(self):
        print self.__dict__
class Sl(Person):#少林
    def __init__(self,hp,mp):
        super(Sl,self).__init__(hp,mp)
        self.att = 2 * 10

class Wd(Person):#武当
    def __init__(self,hp,mp):
        super(Wd,self).__init__(hp,mp)
        self.att = 2 * randint(5,15)

class Hs(Person):#华山
    def __init__(self,hp,mp):
        super(Hs,self).__init__(hp,mp)
        self.att = 2 * randint(0,20)

class Mj(Person):#魔教
    def __init__(self,hp,mp):
        super(Mj,self).__init__(hp,mp)
        self.att = randint(1,3) * randint(0,20)

boss = Mj(1000,1000)

if shape == 1:
    a=randint(100,500)
    b=randint(100,500)
elif shape == 2:
    a=randint(50,100)
    b=randint(50,100)
else:
    a=randint(0,50)
    b=randint(0,50)

if team == 1:
    modada = Sl(a,b)
elif team == 2:
    modada = Wd(a,b)
elif team == 3:
    modada = Hs(a,b)
else:
    modada = Mj(a,b)

def combat():
    '''耐心点,胜利属于坚持.小提示,可以多休息多治疗几次,没有上限的'''
    action = raw_input("1攻击,2疗伤,3休息,4查看> ")
    if action == "1":
        modada.mp -= 10
        modada.hp -= boss.att
        boss.hp -= modada.att
    elif action == "2":
        modada.heal()
    elif action == "3":
        modada.rest()
    elif action == "4":
        modada.check()
    else:
        print combat.__doc__

while True: 
    combat()
    if modada.mp <20 and modada.mp >0:
        print "莫大大筋疲力尽"
    elif modada.mp <0:
        print "莫大大精尽人亡"
        exit(1)
    elif modada.hp <0:
        print "莫大大流尽了最后一滴血"
        exit(1)
    elif boss.hp <0 and modada.hp >0:
        print "莫大大打败了boss"
        print "独立苍茫每怅然，恩仇一例付云烟，断鸿零雁剩残篇。莫道萍踪随逝水，永存侠影在心田，此中心事倩谁传。"
        exit(0)

