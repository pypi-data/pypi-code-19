# -*- coding=utf-8 -*-

def full_url(url, param):
    p = ''
    for k, v in param.items():
        p = '%s&%s=%s' % (p, k, v)
    full = '%s?%s' % (url, p)
    return full


#
# if __name__ == '__main__':
#     url = 'https://apphouse.58.com/api/list/hezu?&localname=bj&os=android&format=json&v=1&geotype=baidu&page=2'
#
#     param = {
#         'action':'getListInfo',
#         'curVer': '7.13.1',
#         'appId':'1'
#     }
#
#     print(full_url(url, param))