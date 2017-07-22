#coding:utf-8

import pandas as pd
import os
import subprocess as sp
import time
ip_rd=pd.read_excel('ips.xls')
ips=list(ip_rd['ips'])
# ips=['www.baidu.com']
# print(ips)
# ips=['www.baidu.com']
# df=pd.DataFrame()
# routes=[]
# rt_time=[]
ct=0
print(ips)
df = pd.DataFrame()

while True:
    for ip in ips:
        rt = sp.Popen('tracert -h 10 %s' % ip, shell=False, stdout=sp.PIPE).stdout
        # routes.append(rt.readlines())
        # rt_time.append(time.strftime('%Y-%m-%d %H-%M-%S'))
        df = df.append({'routes': rt.readlines(), 'rt_time': time.strftime('%Y-%m-%d %H:%M'),'ip':ip}, ignore_index=True)
        print(ip+' tracert at %s' % time.strftime('%Y-%m-%d %H:%M'))
        # df=df.append({'routes':'222'},ignore_index=True)
    ct = ct + 1
    if ct%12==0:
        df.to_excel('tracert_test%d.xls'%ct, time.strftime('%Y-%m-%d'))
        print('tracert_to_excel succeed!')
        df = pd.DataFrame()
        # df.pop('routes')time.strftime('%Y-%m-%d')
    if ct==168:
        break
    time.sleep(60*60)

        # rt=sp.Popen('tracert -h 3 www.baidu.com',shell=False,stdout=sp.PIPE)
# (stdout,stderr)=rt.communicate()
# print(stdout)
# print(time.strftime('%Y-%m-%d'))
# print(routes)