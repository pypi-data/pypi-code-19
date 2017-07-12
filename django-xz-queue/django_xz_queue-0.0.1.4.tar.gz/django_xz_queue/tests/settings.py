# -*- coding: utf-8 -*-


INSTALLED_APPS = ['django_xz_queue']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}


ENDPOINT = 'http://1409862822082731.mns.cn-hangzhou-internal.aliyuncs.com/'
ACCID = 'l5WmuTAyLtAnzja2'
ACCKEY = 'vkIYT9PRPaIMmerlwfzoZ7Fod5N2BC'

XZ_QUEUES = {
    'sms-send': {
        'QUEUE_TYPE': 'mns', # queue type msn-> aliyun
        'QUEUE_CONSUMER_MODULE': 'web.queue_consumers_function.send_msg', # consumer module
        'QUEUE_CONNECTION': {  # queue save
            'ENDPOINT': ENDPOINT,
            'ACCID': ACCID,
            'ACCKEY': ACCKEY
        }
    }
}