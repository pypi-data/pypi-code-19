#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 15:46:49 2017

@author: zhoumingzhen
"""
import json
import requests
from math import * 
import time
import random
    
def _BdCMer(BDcoor):
    """
    mercator = {"x":12940638.98, "y":4838339.82} 
    lonlat = {} 
    lonlat['x'] - mercator['x']/ 20037508.3427892 * 180 = 0
    lonlat['y'] - 180 / math.pi * (2 * math.atan(math.exp((mercator['y']/ 20037508.3427892 * 180) * math.pi / 180)) - math.pi / 2) = 0
    print (lonlat)
    """
    Merx = float(BDcoor[0])*20037508.34/180
    Mery = log(tan((90 + float(BDcoor[1]))*pi/360))/(pi/180)
    Mery = Mery*20037508.34/180
    return Merx,Mery
def addr(BDcoor):
    Merx,Mery = _BdCMer(BDcoor)
    param0 = str(Merx) + ',' + str(Mery)
    #param1 = str(Merx-484) + ',' + str(Mery-333)
    #param2 = str(Merx+484) + ',' + str(Mery-333)
    timeStamp = str(time.time()).replace(".", "")[:13]
    params1 = {
            "newmap" : "1",
            "reqflag" : "pcmap",
            "biz" : "1",
            "from" : "webmap",
            "da_par" : "direct",
            "pcevaname" : "pc4.1",
            "qt" : "s",
            "from" : "webmap",
            "da_src":"searchBox.button",
            "wd" : "",
            "c" : "",
            "src" : "0",
            "wd2" : "",
            "l" : "19",
            "b" : "("+param0+";"+param0+")",
            "from":"webmap",
            "biz_forward":"{%22scaler%22:1,%22styles%22:%22pl%22}",
            "sug_forward":"",
            "tn":"B_NORMAL_MAP",
            "nn":"0",
            "u_loc" : param0,
            "ie" : "utf-8",
            "t" : timeStamp
            }
       
    ajaxquery="http://map.baidu.com/"
    response=requests.get(ajaxquery,params=params1)
    result = json.loads(response.text)
    #print(result)    
    #print(result)
    #http://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=spot&from=webmap&c=267&wd=%E7%BE%8E%E9%A3%9F&wd2=&pn=0&nn=0&db=0&sug=0&addr=0&pl_data_type=cater&pl_sub_type=&pl_price_section=0%2C%2B&pl_sort_type=data_type&pl_sort_rule=0&pl_discount2_section=0%2C%2B&pl_groupon_section=0%2C%2B&pl_cater_book_pc_section=0%2C%2B&pl_hotel_book_pc_section=0%2C%2B&pl_ticket_book_flag_section=0%2C%2B&pl_movie_book_section=0%2C%2B&pl_business_type=cater&pl_business_id=&da_src=pcmappg.poi.page&on_gel=1&src=7&gr=3&l=12&rn=50&tn=B_NORMAL_MAP&u_loc=12952552,4849496&ie=utf-8&b=(12936232,4826168;12946600,4872824)&t=1496908990256
    #http://map.baidu.com/?newmap=1&reqflag=pcmap&biz=1&from=webmap&da_par=direct&pcevaname=pc4.1&qt=spot&from=webmap&c=267&wd=%E8%A1%97%E9%81%93&wd2=&pn=0&nn=0&db=0&sug=0&addr=0&pl_data_type=cater&pl_sub_type=&pl_price_section=0%2C%2B&pl_sort_type=data_type&pl_sort_rule=0&pl_discount2_section=0%2C%2B&pl_groupon_section=0%2C%2B&pl_cater_book_pc_section=0%2C%2B&pl_hotel_book_pc_section=0%2C%2B&pl_ticket_book_flag_section=0%2C%2B&pl_movie_book_section=0%2C%2B&pl_business_type=cater&pl_business_id=&da_src=pcmappg.poi.page&on_gel=1&src=7&gr=3&l=12&rn=50&tn=B_NORMAL_MAP&u_loc=12727992,4258772&ie=utf-8&b=(12727992-50,4258772-50;12727992+50,4258772+50)&t=1496908990256
    province = result['current_city']['up_province_name']
    city = result['current_city']['name']
    city_code = result['current_city']['code']
    threshold = 50
    poi = "街道"
    reginal1 = str(Merx-threshold) + ',' + str(Mery-threshold)
    reginal2 = str(Merx+threshold) + ',' + str(Mery+threshold)
    params2 = {
            "newmap" : "1",
            "reqflag" : "pcmap",
            "biz" : "1",
            "from" : "webmap",
            "da_par" : "direct",
            "pcevaname" : "pc4.1",
            "qt" : "spot",
            "from" : "webmap",
            "c" : city_code,
            "wd" : poi,
            "wd2" : "",
            "pn":0,
            "nn":0,
            "db":0,
            "sug":0,
            "addr":0,
            "pl_data_type":"cater",
            "pl_sub_type":"",
            "pl_price_section":"0%2C%2B",
            "pl_sort_type":"data_type",
            "pl_sort_rule":"0",
            "pl_discount2_section":"0%2C%2B",
            "pl_groupon_section":"0%2C%2B",
            "pl_cater_book_pc_section":"0%2C%2B",
            "pl_hotel_book_pc_section":"0%2C%2B",
            "pl_ticket_book_flag_section":"0%2C%2B",
            "pl_movie_book_section":"0%2C%2B",
            "pl_business_type":"cater",
            "pl_business_id":"",
            "da_src":"pcmappg.poi.page",
            "on_gel":"1",
            "src":"7",
            "gr":"3",
            "l":"19",
            "rn":"50",
            "tn":"B_NORMAL_MAP",
            "b" : reginal1+";"+reginal2,
            "u_loc" : param0,
            "ie" : "utf-8",
            "t" : timeStamp
            }
       
    response=requests.get(ajaxquery,params=params2)
    result = json.loads(response.text)
    district = result['content'][0]['area_name']
    street = result['content'][0]['addr']
    return (province,city,district,street)

def detaddr(BDcoor):
    Merx,Mery = _BdCMer(BDcoor)
    rand1 = random.randint(1,10)
    rand2 = random.randint(10,20)
    params = {
            "qt":"rgc",
            "x":"%.2f" %Merx,
            "y":"%.2f" %Mery,
            "dis_poi":rand1,
            "poi_num":rand2,
            "ie":"utf-8",
            "oue":"1",
            "fromproduct":"jsapi",
            "res":"",
            "callback":"" 
            }    
    ajaxquery="http://api.map.baidu.com/"
    response=requests.get(ajaxquery,params=params)
    result = json.loads(response.text)
    detaddr = {}
    detaddr['country'] = result['content']['address_detail']['country']
    detaddr['province'] = result['content']['address_detail']['province']
    detaddr['city'] = result['content']['address_detail']['city']
    detaddr['district'] = result['content']['address_detail']['district']
    detaddr['adcode'] = result['content']['address_detail']['adcode']
    detaddr['street'] = result['content']['address_detail']['street']
    detaddr['street_number'] = result['content']['address_detail']['street_number']
    detaddr['point'] = result['content']['point']
    detaddr['address'] = result['content']['address']
    return detaddr
# http://api.map.baidu.com/?qt=rgc&x=12952036.89&y=4838678.38&dis_poi=100&poi_num=10&ie=utf-8&oue=1&fromproduct=jsapi&res=api&callback=BMap._rd._cbk16238&ak=E4805d16520de693a3fe707cdc962045                                                                                                                                                            





if __name__ == '__main__':
    BDcoor = (119.727986,36.33307)
    print(addr(BDcoor))
    print(detaddr(BDcoor))
